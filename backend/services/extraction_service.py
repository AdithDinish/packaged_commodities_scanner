import re
import sys
from pathlib import Path

# Add backend and backend/ai to path
BACKEND_DIR = Path(__file__).parent.parent
sys.path.append(str(BACKEND_DIR))
sys.path.append(str(BACKEND_DIR / "ai"))

from text_normalizer import detect_field


def extract_declarations(ocr_data):
    """
    Extracts mandatory commodity declarations from OCR text tokens and layout boxes.
    """
    texts = [str(t).strip() for t in ocr_data.get("rec_texts", []) if str(t).strip()]
    full_text = "\n".join(texts)

    declarations = {
        "product_name": "",
        "brand": "",
        "manufacturer": "",
        "manufacturer_address": "",
        "net_quantity": "",
        "mrp": "",
        "unit_sale_price": "",
        "batch_number": "",
        "manufacturing_date": "",
        "expiry_date": "",
        "best_before": "",
        "consumer_care": "",
        "country_of_origin": ""
    }

    # 1. Product Name & Brand
    for text in texts:
        lower = text.lower()
        if any(k in lower for k in ["special mixture", "biscui", "namkeen", "chips", "oil", "flour", "atta", "rice", "tea", "coffee"]):
            declarations["product_name"] = text
            break

    for text in texts:
        lower = text.lower()
        if lower in ["saga", "nestle", "britannia", "amul", "haldiram", "parle", "tata"]:
            declarations["brand"] = text.title()
            break

    # If product name or brand still empty, pick top lines
    if not declarations["product_name"] and len(texts) > 1:
        declarations["product_name"] = texts[1]
    if not declarations["brand"] and len(texts) > 0:
        declarations["brand"] = texts[0]

    # 2. Manufacturer & Address
    mfg_idx = None
    for i, text in enumerate(texts):
        if "manufactured" in text.lower() or "packaged by" in text.lower() or "packed by" in text.lower():
            mfg_idx = i
            break

    if mfg_idx is not None:
        # Check next line for Company Name
        if mfg_idx + 1 < len(texts):
            declarations["manufacturer"] = texts[mfg_idx + 1]

        # Aggregate address lines
        addr_parts = []
        for text in texts[mfg_idx + 1:]:
            lower = text.lower()
            if "marketed by" in lower or "net" in lower or "mrp" in lower or "customer care" in lower:
                break
            if any(k in lower for k in ["road", "street", "village", "taluk", "dist", "state", "india", "pincode", "-6", "pvt", "ltd"]):
                if text != declarations["manufacturer"]:
                    addr_parts.append(text)

        declarations["manufacturer_address"] = " ".join(addr_parts)
    else:
        # Search for company name pattern
        for text in texts:
            if re.search(r"\b(pvt|ltd|limited|private|industries|foods)\b", text, re.IGNORECASE):
                declarations["manufacturer"] = text
                break

    # 3. Net Quantity
    net_patterns = [r"net\s*(?:weight|wight|quantity|qty|wt)", r"\b\d+(?:\.\d+)?\s*(?:kg|g|mg|ml|l|n)\b"]
    for i, text in enumerate(texts):
        lower = text.lower()
        if any(re.search(p, lower) for p in net_patterns):
            # Extract number + unit
            match = re.search(r"(\d+(?:\.\d+)?)\s*(kg|g|mg|ml|l|n|pcs|units?)\b", text, re.IGNORECASE)
            if match:
                declarations["net_quantity"] = f"{match.group(1)} {match.group(2)}"
                break
            # Check next lines
            for next_text in texts[i+1:i+3]:
                match = re.search(r"(\d+(?:\.\d+)?)\s*(kg|g|mg|ml|l|n|pcs|units?)\b", next_text, re.IGNORECASE)
                if match:
                    declarations["net_quantity"] = f"{match.group(1)} {match.group(2)}"
                    break
            if declarations["net_quantity"]:
                break

    # 4. MRP
    for i, text in enumerate(texts):
        lower = text.lower().strip()
        if any(k in lower for k in ["mr", "mrp", "m.r.p", "price", "max retail"]):
            # Look for currency figure
            match = re.search(r"(?:rs\.?|₹)?\s*(\d+(?:\.\d+)?)", text, re.IGNORECASE)
            if match and float(match.group(1)) > 0:
                declarations["mrp"] = f"₹ {match.group(1)}"
                break
            for next_text in texts[i+1:i+3]:
                match = re.search(r"(?:rs\.?|₹)?\s*(\d+(?:\.\d+)?)", next_text, re.IGNORECASE)
                if match and float(match.group(1)) > 0:
                    declarations["mrp"] = f"₹ {match.group(1)}"
                    break
            if declarations["mrp"]:
                break

    # 5. Unit Sale Price (USP)
    for text in texts:
        if "usp" in text.lower() or "unit price" in text.lower() or re.search(r"(?:rs|₹).*(?:per|\/)", text, re.IGNORECASE):
            declarations["unit_sale_price"] = text
            break

    # 6. Batch Number
    for i, text in enumerate(texts):
        lower = text.lower()
        if "batch" in lower or "bat no" in lower or "lot no" in lower or "b.no" in lower:
            match = re.search(r"(?:batch|bat|lot|b\.?no)\.?\s*[:\-]?\s*([A-Za-z0-9\/\-]+)", text, re.IGNORECASE)
            if match and match.group(1).lower() not in ["no", "number"]:
                declarations["batch_number"] = match.group(1)
                break
            for next_text in texts[i+1:i+3]:
                candidate = next_text.strip()
                if re.fullmatch(r"[A-Za-z0-9\/\-]+", candidate) and candidate.lower() not in ["no"]:
                    declarations["batch_number"] = candidate
                    break
            if declarations["batch_number"]:
                break

    # 7. Dates (Manufacturing / Expiry)
    for text in texts:
        lower = text.lower()
        if "mfg" in lower or "manufacture" in lower or "pkd" in lower or "packed" in lower:
            match = re.search(r"\b(?:\d{1,2}[\/\-]\d{2,4}|[A-Za-z]{3,9}\s*\d{2,4})\b", text)
            if match:
                declarations["manufacturing_date"] = match.group(0)
        if "exp" in lower or "expiry" in lower or "use by" in lower:
            match = re.search(r"\b(?:\d{1,2}[\/\-]\d{2,4}|[A-Za-z]{3,9}\s*\d{2,4})\b", text)
            if match:
                declarations["expiry_date"] = match.group(0)

    # 8. Consumer Care
    cc_parts = []
    for i, text in enumerate(texts):
        lower = text.lower()
        if any(k in lower for k in ["customer care", "consumer care", "feedback", "complaints", "helpline"]):
            for cand in texts[max(0, i-1):min(len(texts), i+4)]:
                cc_parts.append(cand)
            break

    declarations["consumer_care"] = " ".join(cc_parts) if cc_parts else ""

    # 9. Country of Origin
    for text in texts:
        lower = text.lower()
        if "made in india" in lower or "country of origin: india" in lower or "product of india" in lower:
            declarations["country_of_origin"] = "India"
            break
        elif "country of origin" in lower:
            declarations["country_of_origin"] = text.split(":")[-1].strip()
            break

    return declarations, full_text
