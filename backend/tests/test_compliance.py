import pytest
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent
sys.path.append(str(BACKEND_DIR))

from compliance.rules_engine import LegalMetrologyRulesEngine
from compliance.evaluator import evaluate_compliance


def test_rule_mrp_valid():
    declarations = {"mrp": "₹ 65.00"}
    raw_text = "MR: ₹ 65.00 Incl. of all taxes"
    result = LegalMetrologyRulesEngine.check_mrp(declarations, raw_text)
    assert result["status"] == "COMPLIANT"
    assert result["rule_code"] == "R5_MRP"


def test_rule_mrp_missing_tax_clause():
    declarations = {"mrp": "₹ 65.00"}
    raw_text = "MR: ₹ 65.00"
    result = LegalMetrologyRulesEngine.check_mrp(declarations, raw_text)
    assert result["status"] == "NON_COMPLIANT"


def test_rule_net_quantity_valid():
    declarations = {"net_quantity": "250 g"}
    result = LegalMetrologyRulesEngine.check_net_quantity(declarations)
    assert result["status"] == "COMPLIANT"


def test_compliance_evaluator_aggregator():
    declarations = {
        "product_name": "Special Mixture",
        "brand": "Saga",
        "manufacturer": "CRN FOODS Pvt. Ltd.",
        "manufacturer_address": "66/2 B4 Krishnagiri Main Road, Dharmapuri - 635 205. Tamilnadu, INDIA",
        "net_quantity": "250 g",
        "mrp": "₹ 65.00",
        "unit_sale_price": "₹ 0.26 per g",
        "batch_number": "B-4092",
        "manufacturing_date": "08/2026",
        "consumer_care": "Helpline: +91 90666 22332, Email: info@sagafoods.in",
        "country_of_origin": "India"
    }

    raw_text = "Saga Special Mixture CRN FOODS Pvt. Ltd. Net Weight: 250 g MR: ₹ 65.00 Incl. of all taxes USP: ₹ 0.26 per g Helpline: +91 90666 22332 info@sagafoods.in Country of Origin: India"
    ocr_data = {"rec_texts": ["Saga", "250 g"], "rec_boxes": [[10, 10, 50, 30], [60, 60, 100, 80]]}

    res = evaluate_compliance(declarations, ocr_data, raw_text)

    assert res["overall_status"] in ["COMPLIANT", "WARNING", "NON_COMPLIANT"]
    assert res["compliance_score"] > 0
    assert len(res["rules"]) == 9
