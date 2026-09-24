import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from rules_engine import LegalMetrologyRulesEngine


def evaluate_compliance(declarations, ocr_data, raw_text="", img_width=800, img_height=1000):
    """
    Evaluates extracted product declarations against Legal Metrology (Packaged Commodities) Rules, 2011.
    Calculates score, status, rule violations, and visual bounding box annotations.
    """
    rules = [
        LegalMetrologyRulesEngine.check_manufacturer(declarations),
        LegalMetrologyRulesEngine.check_product_name(declarations),
        LegalMetrologyRulesEngine.check_net_quantity(declarations),
        LegalMetrologyRulesEngine.check_mfg_date(declarations),
        LegalMetrologyRulesEngine.check_mrp(declarations, raw_text),
        LegalMetrologyRulesEngine.check_unit_sale_price(declarations, raw_text),
        LegalMetrologyRulesEngine.check_consumer_care(declarations),
        LegalMetrologyRulesEngine.check_country_of_origin(declarations),
        LegalMetrologyRulesEngine.check_font_size(ocr_data, img_width, img_height)
    ]

    total_rules = len(rules)
    passed_rules = sum(1 for r in rules if r["status"] == "COMPLIANT")
    warning_rules = sum(1 for r in rules if r["status"] == "WARNING")
    failed_rules = sum(1 for r in rules if r["status"] == "NON_COMPLIANT")

    # Weighted Compliance Score (0 - 100%)
    score = round(((passed_rules * 1.0 + warning_rules * 0.5) / total_rules) * 100, 1)

    # Determine overall inspection status
    if failed_rules > 0:
        overall_status = "NON_COMPLIANT"
    elif warning_rules > 0:
        overall_status = "WARNING"
    else:
        overall_status = "COMPLIANT"

    # Map OCR bounding boxes with compliance annotations
    boxes = ocr_data.get("rec_boxes", [])
    texts = ocr_data.get("rec_texts", [])

    annotated_boxes = []

    for text, box in zip(texts, boxes):
        text_str = str(text).strip()
        if not text_str or len(box) != 4:
            continue

        lower = text_str.lower()
        box_color = "#3B82F6"  # Neutral blue default
        box_status = "INFO"
        matched_field = None

        # Check if text corresponds to a failed or compliant rule field
        if any(k in lower for k in ["mr", "mrp", "rs", "price", "inclusive"]):
            matched_field = "MRP"
            mrp_rule = next((r for r in rules if r["rule_code"] == "R5_MRP"), None)
            if mrp_rule and mrp_rule["status"] == "NON_COMPLIANT":
                box_color = "#EF4444"  # Red
                box_status = "NON_COMPLIANT"
            else:
                box_color = "#10B981"  # Green
                box_status = "COMPLIANT"

        elif any(k in lower for k in ["net", "weight", "qty", "quantity", "g", "kg", "ml"]):
            matched_field = "Net Quantity"
            qty_rule = next((r for r in rules if r["rule_code"] == "R3_NET_QTY"), None)
            if qty_rule and qty_rule["status"] == "NON_COMPLIANT":
                box_color = "#EF4444"
                box_status = "NON_COMPLIANT"
            else:
                box_color = "#10B981"
                box_status = "COMPLIANT"

        elif any(k in lower for k in ["manufactured", "packaged", "mfd", "crn foods", "pvt ltd"]):
            matched_field = "Manufacturer"
            mfg_rule = next((r for r in rules if r["rule_code"] == "R1_MANUFACTURER"), None)
            if mfg_rule and mfg_rule["status"] == "NON_COMPLIANT":
                box_color = "#EF4444"
                box_status = "NON_COMPLIANT"
            elif mfg_rule and mfg_rule["status"] == "WARNING":
                box_color = "#F59E0B"
                box_status = "WARNING"
            else:
                box_color = "#10B981"
                box_status = "COMPLIANT"

        elif any(k in lower for k in ["customer care", "complaints", "email", "+91"]):
            matched_field = "Consumer Care"
            cc_rule = next((r for r in rules if r["rule_code"] == "R7_CONSUMER_CARE"), None)
            if cc_rule and cc_rule["status"] == "NON_COMPLIANT":
                box_color = "#EF4444"
                box_status = "NON_COMPLIANT"
            elif cc_rule and cc_rule["status"] == "WARNING":
                box_color = "#F59E0B"
                box_status = "WARNING"
            else:
                box_color = "#10B981"
                box_status = "COMPLIANT"

        annotated_boxes.append({
            "text": text_str,
            "box": box,  # [x1, y1, x2, y2]
            "field": matched_field,
            "status": box_status,
            "color": box_color
        })

    return {
        "overall_status": overall_status,
        "compliance_score": score,
        "total_rules": total_rules,
        "passed_rules": passed_rules,
        "failed_rules": failed_rules,
        "warning_rules": warning_rules,
        "rules": rules,
        "annotated_boxes": annotated_boxes
    }
