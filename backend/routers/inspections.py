from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import uuid
import json
from datetime import datetime

import sys
BACKEND_DIR = Path(__file__).parent.parent
sys.path.append(str(BACKEND_DIR))

from database.database import get_db
from database.models import Inspection
from services.ocr_service import ocr_service_instance
from services.extraction_service import extract_declarations
from compliance.evaluator import evaluate_compliance
from services.report_generator import generate_compliance_report

router = APIRouter(prefix="/api", tags=["Legal Metrology Inspections"])

UPLOAD_DIR = BACKEND_DIR / "uploads"
REPORT_DIR = BACKEND_DIR / "reports"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/scan")
async def scan_package_image(
    file: UploadFile = File(...),
    inspector_name: str = Query("Official Inspector (DoCA)"),
    db: Session = Depends(get_db)
):
    """
    Ingests package image upload, performs OCR, extracts commodity declarations,
    runs Legal Metrology (Packaged Commodities) Rules 2011 evaluation engine,
    generates PDF report, and persists inspection record to database.
    """
    ext = Path(file.filename).suffix or ".jpg"
    unique_filename = f"{uuid.uuid4().hex[:10]}_{file.filename}"
    saved_image_path = UPLOAD_DIR / unique_filename

    # Save uploaded image
    with saved_image_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 1. Run OCR Engine
    ocr_data = ocr_service_instance.process_image(saved_image_path)

    # 2. Extract Commodity Declarations
    declarations, raw_text = extract_declarations(ocr_data)

    # 3. Legal Metrology Rules 2011 Compliance Evaluation
    eval_result = evaluate_compliance(
        declarations=declarations,
        ocr_data=ocr_data,
        raw_text=raw_text,
        img_width=ocr_data.get("img_width", 800),
        img_height=ocr_data.get("img_height", 1000)
    )

    # Generate Scan Reference Code
    scan_ref = f"LM-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    # 4. Generate PDF Report
    pdf_filename = f"Inspection_Report_{scan_ref}.pdf"
    pdf_filepath = REPORT_DIR / pdf_filename

    report_payload = {
        "scan_ref": scan_ref,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "inspector_name": inspector_name,
        "product_name": declarations.get("product_name", "Packaged Commodity"),
        "brand": declarations.get("brand", "Generic Brand"),
        "overall_status": eval_result["overall_status"],
        "compliance_score": eval_result["compliance_score"],
        "passed_rules": eval_result["passed_rules"],
        "rules": eval_result["rules"]
    }

    try:
        generate_compliance_report(report_payload, pdf_filepath)
        pdf_rel_path = f"/reports/{pdf_filename}"
    except Exception as e:
        print(f"Error generating report PDF: {e}")
        pdf_rel_path = None

    # 5. Save Record to Database
    inspection = Inspection(
        scan_ref=scan_ref,
        inspector_name=inspector_name,
        product_name=declarations.get("product_name", "Packaged Commodity"),
        brand=declarations.get("brand", "Generic Brand"),
        category="Food / Retail Package",
        image_filename=unique_filename,
        image_path=f"/uploads/{unique_filename}",
        report_path=pdf_rel_path,
        overall_status=eval_result["overall_status"],
        compliance_score=eval_result["compliance_score"],
        total_rules=eval_result["total_rules"],
        passed_rules=eval_result["passed_rules"],
        failed_rules=eval_result["failed_rules"],
        warning_rules=eval_result["warning_rules"],
        declarations_json=declarations,
        violations_json=eval_result["rules"],
        ocr_data_json=ocr_data,
        bounding_boxes_json=eval_result["annotated_boxes"]
    )

    db.add(inspection)
    db.commit()
    db.refresh(inspection)

    return {
        "status": "success",
        "id": inspection.id,
        "scan_ref": scan_ref,
        "created_at": inspection.created_at.strftime("%Y-%m-%d %H:%M:%S") if inspection.created_at else str(datetime.now()),
        "inspector_name": inspector_name,
        "product_name": inspection.product_name,
        "brand": inspection.brand,
        "image_url": inspection.image_path,
        "report_url": pdf_rel_path,
        "overall_status": eval_result["overall_status"],
        "compliance_score": eval_result["compliance_score"],
        "passed_rules": eval_result["passed_rules"],
        "failed_rules": eval_result["failed_rules"],
        "warning_rules": eval_result["warning_rules"],
        "declarations": declarations,
        "rules_evaluation": eval_result["rules"],
        "bounding_boxes": eval_result["annotated_boxes"]
    }


@router.get("/inspections")
def list_inspections(
    search: str = Query(None),
    status: str = Query(None),
    limit: int = Query(50),
    db: Session = Depends(get_db)
):
    """
    Returns list of scanned products and inspection history.
    Supports search filtering by brand/product title and compliance status.
    """
    query = db.query(Inspection)
    if status and status.upper() != "ALL":
        query = query.filter(Inspection.overall_status == status.upper())
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (Inspection.product_name.like(search_fmt)) |
            (Inspection.brand.like(search_fmt)) |
            (Inspection.scan_ref.like(search_fmt))
        )

    records = query.order_by(Inspection.id.desc()).limit(limit).all()

    return [{
        "id": r.id,
        "scan_ref": r.scan_ref,
        "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else None,
        "inspector_name": r.inspector_name,
        "product_name": r.product_name,
        "brand": r.brand,
        "overall_status": r.overall_status,
        "compliance_score": r.compliance_score,
        "passed_rules": r.passed_rules,
        "failed_rules": r.failed_rules,
        "warning_rules": r.warning_rules,
        "image_url": r.image_path,
        "report_url": r.report_path
    } for r in records]


@router.get("/inspections/{inspection_id}")
def get_inspection_detail(inspection_id: int, db: Session = Depends(get_db)):
    """
    Returns complete detailed inspection record including extracted text and bounding boxes.
    """
    record = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Inspection record not found")

    return {
        "id": record.id,
        "scan_ref": record.scan_ref,
        "created_at": record.created_at.strftime("%Y-%m-%d %H:%M:%S") if record.created_at else None,
        "inspector_name": record.inspector_name,
        "product_name": record.product_name,
        "brand": record.brand,
        "overall_status": record.overall_status,
        "compliance_score": record.compliance_score,
        "passed_rules": record.passed_rules,
        "failed_rules": record.failed_rules,
        "warning_rules": record.warning_rules,
        "image_url": record.image_path,
        "report_url": record.report_path,
        "declarations": record.declarations_json,
        "rules_evaluation": record.violations_json,
        "bounding_boxes": record.bounding_boxes_json
    }


@router.get("/inspections/{inspection_id}/report")
def download_inspection_report(inspection_id: int, db: Session = Depends(get_db)):
    """
    Downloads digital PDF compliance report.
    """
    record = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not record or not record.report_path:
        raise HTTPException(status_code=404, detail="Report PDF not found")

    full_pdf_path = BACKEND_DIR / record.report_path.lstrip("/")
    if not full_pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF report file does not exist on server")

    return FileResponse(
        path=str(full_pdf_path),
        media_type="application/pdf",
        filename=full_pdf_path.name
    )


@router.get("/dashboard/stats")
def get_dashboard_statistics(db: Session = Depends(get_db)):
    """
    Aggregates inspection analytics for enforcement officials.
    """
    total_scans = db.query(Inspection).count()
    compliant_count = db.query(Inspection).filter(Inspection.overall_status == "COMPLIANT").count()
    non_compliant_count = db.query(Inspection).filter(Inspection.overall_status == "NON_COMPLIANT").count()
    warning_count = db.query(Inspection).filter(Inspection.overall_status == "WARNING").count()

    compliance_rate = round((compliant_count / max(total_scans, 1)) * 100, 1)

    # Top violated rules aggregation
    all_inspections = db.query(Inspection).all()
    violation_counts = {}
    for insp in all_inspections:
        rules = insp.violations_json or []
        for r in rules:
            if r.get("status") in ["NON_COMPLIANT", "WARNING"]:
                code = r.get("rule_name", r.get("rule_code"))
                violation_counts[code] = violation_counts.get(code, 0) + 1

    sorted_violations = sorted(
        [{"rule": k, "count": v} for k, v in violation_counts.items()],
        key=lambda x: x["count"],
        reverse=True
    )

    return {
        "total_scans": total_scans,
        "compliant_count": compliant_count,
        "non_compliant_count": non_compliant_count,
        "warning_count": warning_count,
        "compliance_rate": compliance_rate,
        "top_violations": sorted_violations[:5]
    }


@router.get("/rules")
def get_rules_catalog():
    """
    Returns legal reference catalog for Legal Metrology (Packaged Commodities) Rules, 2011.
    """
    return [
        {
            "code": "R1_MANUFACTURER",
            "name": "Manufacturer/Packer/Importer Details",
            "section": "Rule 6(1)(a)",
            "description": "Name and complete address of the manufacturer, packer, or importer.",
            "severity": "CRITICAL"
        },
        {
            "code": "R2_PRODUCT_NAME",
            "name": "Generic/Common Name of Commodity",
            "section": "Rule 6(1)(b)",
            "description": "Generic or common name of the commodity packaged inside.",
            "severity": "CRITICAL"
        },
        {
            "code": "R3_NET_QTY",
            "name": "Net Quantity Declaration",
            "section": "Rule 6(1)(c) & Schedule II",
            "description": "Net quantity in standard metric SI units (g, kg, ml, l, N, pcs).",
            "severity": "CRITICAL"
        },
        {
            "code": "R4_MFG_DATE",
            "name": "Month & Year of Manufacture/Packing",
            "section": "Rule 6(1)(d)",
            "description": "Month and year in which commodity was manufactured, packed, or imported.",
            "severity": "CRITICAL"
        },
        {
            "code": "R5_MRP",
            "name": "Maximum Retail Price (MRP) Declaration",
            "section": "Rule 6(1)(e)",
            "description": "MRP in Rupees inclusive of all taxes ('Incl. of all taxes').",
            "severity": "CRITICAL"
        },
        {
            "code": "R6_UNIT_PRICE",
            "name": "Unit Sale Price (USP) Declaration",
            "section": "Rule 6(1)(n)",
            "description": "Mandatory unit price per gram/ml/kg/l/item on bulk/multi-unit packages.",
            "severity": "MAJOR"
        },
        {
            "code": "R7_CONSUMER_CARE",
            "name": "Consumer Care Helpline & Contact",
            "section": "Rule 6(2)",
            "description": "Name/Designation, Telephone Helpline, and Email Address for consumer grievances.",
            "severity": "CRITICAL"
        },
        {
            "code": "R8_COUNTRY_ORIGIN",
            "name": "Country of Origin Declaration",
            "section": "Rule 6(1)(m)",
            "description": "Country of origin tag for imported or domestic packaged commodities.",
            "severity": "MAJOR"
        },
        {
            "code": "R9_FONT_SIZE",
            "name": "Font Height & Readability Compliance",
            "section": "Rule 7 & Schedule III",
            "description": "Minimum letter and numeral height relative to principal display panel area.",
            "severity": "MINOR"
        }
    ]
