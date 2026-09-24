from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.sql import func
import sys
from pathlib import Path

from .database import Base


class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scan_ref = Column(String(50), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    inspector_name = Column(String(100), default="Official Inspector (DoCA)")

    # Product Metadata
    product_name = Column(String(200), default="Unknown Product")
    brand = Column(String(100), default="Unknown Brand")
    category = Column(String(100), default="General Packaged Commodity")
    barcode = Column(String(50), nullable=True)

    # Scanned Assets
    image_filename = Column(String(200))
    image_path = Column(String(500))
    report_path = Column(String(500), nullable=True)

    # Compliance Evaluation
    overall_status = Column(String(30))  # COMPLIANT, NON_COMPLIANT, WARNING
    compliance_score = Column(Float, default=0.0)  # 0 to 100 percentage
    total_rules = Column(Integer, default=9)
    passed_rules = Column(Integer, default=0)
    failed_rules = Column(Integer, default=0)
    warning_rules = Column(Integer, default=0)

    # Extracted JSON Data Structures
    declarations_json = Column(JSON)  # Extracted field dictionary
    violations_json = Column(JSON)    # Detailed array of rule evaluation items
    ocr_data_json = Column(JSON)      # Raw text tokens and bounding box metrics
    bounding_boxes_json = Column(JSON) # Color-coded boxes for UI annotation


class RuleCatalog(Base):
    __tablename__ = "rule_catalog"

    id = Column(Integer, primary_key=True, index=True)
    rule_code = Column(String(30), unique=True)
    rule_name = Column(String(200))
    legal_section = Column(String(100))
    description = Column(Text)
    severity = Column(String(20)) # CRITICAL, MAJOR, MINOR
