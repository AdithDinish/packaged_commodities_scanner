import json
import re
from pathlib import Path
import sys
import math

sys.path.append(str(Path(__file__).parent))

from text_normalizer import detect_field


# ============================================================
# FILE
# ============================================================

OCR_FILE = Path(
    "backend/ocr_output/images (1)_res.json"
)


# ============================================================
# LOAD OCR
# ============================================================

with OCR_FILE.open("r", encoding="utf-8") as file:
    data = json.load(file)

texts = data["rec_texts"]
boxes = data["rec_boxes"]


# ============================================================
# CREATE OCR ITEMS
# ============================================================

items = []

for index, (text, box) in enumerate(zip(texts, boxes)):

    text = str(text).strip()

    if not text:
        continue

    x1, y1, x2, y2 = list(box)

    items.append({
        "index": index,
        "text": text,
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2,
        "center_x": (x1 + x2) / 2,
        "center_y": (y1 + y2) / 2
    })


# ============================================================
# FIELD-SPECIFIC VALUE PATTERNS
# ============================================================

PATTERNS = {

    "mrp": [
        r"(?:₹|rs\.?|inr)\s*\d+(?:\.\d+)?",
        r"\d+(?:\.\d+)?\s*(?:rs|rupees)"
    ],

    "net_quantity": [
        r"\b\d+(?:\.\d+)?\s*(?:kg|g|mg|l|ml)\b"
    ],

    "batch_number": [
        # Batch numbers normally contain both letters/numbers
        r"\b(?=[A-Za-z0-9\/\-]*\d)"
        r"[A-Za-z0-9][A-Za-z0-9\/\-]{2,}\b"
    ],

    "manufacturing_date": [
        r"\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b",
        r"\b\d{1,2}[\/\-][A-Za-z]{3,9}[\/\-]\d{2,4}\b",
        r"\b[A-Za-z]{3,9}[\/\-]\d{2,4}\b"
    ],

    "expiry_date": [
        r"\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b",
        r"\b\d{1,2}[\/\-][A-Za-z]{3,9}[\/\-]\d{2,4}\b",
        r"\b[A-Za-z]{3,9}[\/\-]\d{2,4}\b"
    ]
}


# ============================================================
# WORDS THAT SHOULD NEVER BE BATCH VALUES
# ============================================================

BATCH_STOP_WORDS = {
    "date",
    "no",
    "number",
    "batch",
    "weight",
    "net",
    "mrp",
    "made",
    "india",
    "use",
    "by"
}


# ============================================================
# FIND VALUE INSIDE TEXT
# ============================================================

def find_value(text, field):

    patterns = PATTERNS.get(field, [])

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if not match:
            continue

        value = match.group(0).strip()

        # Additional protection for batch numbers
        if field == "batch_number":

            if value.lower() in BATCH_STOP_WORDS:
                continue

            # Require at least one digit
            if not re.search(r"\d", value):
                continue

        return value

    return None


# ============================================================
# DISTANCE
# ============================================================

def distance(a, b):

    dx = a["center_x"] - b["center_x"]
    dy = a["center_y"] - b["center_y"]

    return math.sqrt(
        dx * dx + dy * dy
    )


# ============================================================
# FIND FIELD LABELS
# ============================================================

fields = []

for item in items:

    result = detect_field(item["text"])

    if result is None:
        continue

    fields.append({
        "field": result["field"],
        "label": item["text"],
        "confidence": result["confidence"],
        "item": item
    })


# ============================================================
# FIND VALUES
# ============================================================

print()
print("========== FIELD → VALUE MATCHING ==========")
print()


MAX_DISTANCE = 100


for field in fields:

    label_item = field["item"]

    candidates = []

    for item in items:

        if item["index"] == label_item["index"]:
            continue

        value = find_value(
            item["text"],
            field["field"]
        )

        if value is None:
            continue

        dist = distance(
            label_item,
            item
        )

        # Reject distant candidates
        if dist > MAX_DISTANCE:
            continue

        # ----------------------------------------------------
        # Direction
        # ----------------------------------------------------

        dx = item["center_x"] - label_item["center_x"]
        dy = item["center_y"] - label_item["center_y"]

        # Prefer nearby text
        score = dist

        # Small preference for same horizontal/vertical region
        if abs(dy) < 30:
            score -= 20

        if abs(dx) < 30:
            score -= 10

        candidates.append({
            "value": value,
            "source_text": item["text"],
            "distance": round(dist, 2),
            "score": round(score, 2)
        })


    # --------------------------------------------------------
    # Choose best candidate
    # --------------------------------------------------------

    if candidates:

        candidates.sort(
            key=lambda x: x["score"]
        )

        best = candidates[0]

        print(
            f"{field['field']:<25}"
            f" label={field['label']:<15}"
            f" value={best}"
        )

    else:

        print(
            f"{field['field']:<25}"
            f" label={field['label']:<15}"
            f" value=NOT DETECTED"
        )

        