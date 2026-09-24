import json
import re
from pathlib import Path


# ============================================================
# FILES
# ============================================================

OCR_FILE = Path("backend/ocr_output/images (1)_res.json")
OUTPUT_FILE = Path("backend/product_data.json")


# ============================================================
# LOAD OCR DATA
# ============================================================

with OCR_FILE.open("r", encoding="utf-8") as file:
    data = json.load(file)

texts = data.get("rec_texts", [])


# Clean OCR text
texts = [
    str(text).strip()
    for text in texts
    if str(text).strip()
]

full_text = "\n".join(texts)


# ============================================================
# RESULT
# ============================================================

product = {
    "product_name": "",
    "brand": "",
    "manufacturer": "",
    "manufacturer_address": "",
    "net_quantity": "",
    "mrp": "",
    "batch_number": "",
    "manufacturing_date": "",
    "expiry_date": "",
    "best_before": "",
    "consumer_care": "",
    "country_of_origin": ""
}


# ============================================================
# PRODUCT NAME
# ============================================================

for text in texts:
    if "special mixture" in text.lower():
        product["product_name"] = "Special Mixture"
        break


# ============================================================
# BRAND
# ============================================================

for text in texts:
    if text.lower().strip() == "saga":
        product["brand"] = "Saga"
        break


# ============================================================
# MANUFACTURER
# ============================================================

manufacturer_index = None

for i, text in enumerate(texts):

    if "manufactured and packaged" in text.lower():
        manufacturer_index = i
        break


if manufacturer_index is not None:

    # Look at the next few lines after the heading.
    for text in texts[manufacturer_index + 1:manufacturer_index + 5]:

        if "crn foods" in text.lower():
            product["manufacturer"] = "CRN FOODS Pvt. Ltd."
            break


# ============================================================
# MANUFACTURER ADDRESS
# ============================================================

if manufacturer_index is not None:

    address_parts = []

    for text in texts[manufacturer_index + 1:]:

        lower = text.lower()

        # Manufacturer name
        if "crn foods" in lower:
            continue

        # Stop before another major section
        if "marketed by" in lower:
            break

        # Avoid nutrition values
        if re.search(
            r"(calories|total fat|saturated fat|trans fat|cholesterol|sodium|"
            r"carbohydrates|dietary fiber|total sugar|protein|vitamin|calcium|"
            r"iron|potassium)",
            lower
        ):
            continue

        # Address-looking lines
        if (
            re.search(r"\d", text)
            or "village" in lower
            or "taluk" in lower
            or "road" in lower
            or "tamilnadu" in lower
            or "india" in lower
        ):
            address_parts.append(text)

    product["manufacturer_address"] = " ".join(address_parts)


# ============================================================
# NET QUANTITY
# ============================================================

# Look for common OCR variations of "Net Weight"
net_patterns = [
    r"net\s*(?:weight|wight|quantity)",
    r"net\s*w[a-z]*ght"
]

for i, text in enumerate(texts):

    lower = text.lower()

    if any(re.search(pattern, lower) for pattern in net_patterns):

        # Look in same line
        match = re.search(
            r"(\d+(?:\.\d+)?)\s*(kg|g|mg|ml|l)\b",
            text,
            re.IGNORECASE
        )

        if match:
            product["net_quantity"] = (
                f"{match.group(1)} {match.group(2)}"
            )
            break

        # Look at next few OCR lines
        for next_text in texts[i + 1:i + 4]:

            match = re.search(
                r"(\d+(?:\.\d+)?)\s*(kg|g|mg|ml|l)\b",
                next_text,
                re.IGNORECASE
            )

            if match:
                product["net_quantity"] = (
                    f"{match.group(1)} {match.group(2)}"
                )
                break

        if product["net_quantity"]:
            break


# ============================================================
# MRP
# ============================================================

for i, text in enumerate(texts):

    lower = text.lower().strip()

    # OCR often reads MRP incorrectly as "MR"
    if lower in ["mr", "mrp", "m.r.p", "m.r"]:

        for next_text in texts[i + 1:i + 4]:

            match = re.search(
                r"(?:rs\.?|₹)?\s*(\d+(?:\.\d+)?)",
                next_text,
                re.IGNORECASE
            )

            if match:
                product["mrp"] = f"₹{match.group(1)}"
                break

        if product["mrp"]:
            break


# ============================================================
# BATCH NUMBER
# ============================================================

for i, text in enumerate(texts):

    lower = text.lower()

    if (
        "batch" in lower
        or "bat no" in lower
        or lower.strip() == "bat no"
    ):

        # Check same line
        match = re.search(
            r"(?:batch|bat)\s*(?:no|number)?\.?\s*[:\-]?\s*([A-Za-z0-9\/\-]+)",
            text,
            re.IGNORECASE
        )

        if match and match.group(1).lower() not in ["no"]:
            product["batch_number"] = match.group(1)
            break

        # Check following lines
        for next_text in texts[i + 1:i + 3]:

            candidate = next_text.strip()

            if candidate.lower() not in ["no"]:
                if re.fullmatch(
                    r"[A-Za-z0-9\/\-]+",
                    candidate
                ):
                    product["batch_number"] = candidate
                    break

        if product["batch_number"]:
            break


# ============================================================
# COUNTRY OF ORIGIN
# ============================================================

for text in texts:

    if "made in india" in text.lower():
        product["country_of_origin"] = "India"
        break

    if "tamilnadu, india" in text.lower():
        product["country_of_origin"] = "India"
        break


# ============================================================
# CONSUMER CARE
# ============================================================

consumer_parts = []

for i, text in enumerate(texts):

    lower = text.lower()

    if "customer care" in lower:

        for candidate in texts[max(0, i - 2):i + 5]:

            candidate_lower = candidate.lower()

            if (
                "comments" in candidate_lower
                or "complaints" in candidate_lower
                or "customer care" in candidate_lower
                or "+91" in candidate_lower
                or "email" in candidate_lower
                or "info@" in candidate_lower
                or "1800" in candidate_lower
            ):
                consumer_parts.append(candidate)

        break


product["consumer_care"] = " ".join(consumer_parts)


# ============================================================
# SAVE RESULT
# ============================================================

with OUTPUT_FILE.open("w", encoding="utf-8") as file:
    json.dump(
        product,
        file,
        indent=4,
        ensure_ascii=False
    )


# ============================================================
# DISPLAY
# ============================================================

print()
print("========== EXTRACTED PRODUCT DATA ==========")
print()

for key, value in product.items():
    print(f"{key}: {value}")

print()
print("Product data saved to:")
print(OUTPUT_FILE)