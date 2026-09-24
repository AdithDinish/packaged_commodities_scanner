import json
import re
from pathlib import Path
import sys

# Allow importing text_normalizer.py
sys.path.append(str(Path(__file__).parent))

from text_normalizer import detect_field


# ---------------------------------------------------------
# Files
# ---------------------------------------------------------

OCR_FILE = Path(
    "backend/ocr_output/images (1)_res.json"
)


# ---------------------------------------------------------
# Load OCR data
# ---------------------------------------------------------

with OCR_FILE.open("r", encoding="utf-8") as file:
    data = json.load(file)


texts = data["rec_texts"]
boxes = data["rec_boxes"]


# ---------------------------------------------------------
# Convert OCR boxes into normal Python lists
# ---------------------------------------------------------

items = []

for text, box in zip(texts, boxes):

    text = str(text).strip()

    if not text:
        continue

    box = list(box)

    x1, y1, x2, y2 = box

    items.append({
        "text": text,
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2,
        "center_x": (x1 + x2) / 2,
        "center_y": (y1 + y2) / 2
    })


# ---------------------------------------------------------
# Find detected fields
# ---------------------------------------------------------

detected_fields = []


for item in items:

    result = detect_field(item["text"])

    if result is None:
        continue

    detected_fields.append({
        "field": result["field"],
        "confidence": result["confidence"],
        "label": item["text"],
        "center_x": item["center_x"],
        "center_y": item["center_y"]
    })


# ---------------------------------------------------------
# Display results
# ---------------------------------------------------------

print()
print("========== DETECTED FIELDS ==========")
print()

for field in detected_fields:

    print(
        f"{field['field']:<25}"
        f" label={field['label']:<15}"
        f" confidence={field['confidence']}"
        f" position=({field['center_x']:.1f}, "
        f"{field['center_y']:.1f})"
    )


print()
print("Total detected fields:", len(detected_fields))