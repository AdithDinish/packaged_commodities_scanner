import re
from difflib import SequenceMatcher


# ---------------------------------------------------------
# Possible label variations
# ---------------------------------------------------------

FIELD_ALIASES = {
    "mrp": [
        "mrp",
        "m.r.p",
        "m r p",
        "mr"
    ],

    "net_quantity": [
        "net weight",
        "net wight",
        "net wt",
        "net quantity",
        "net qty"
    ],

    "batch_number": [
        "batch no",
        "batch number",
        "bat no",
        "batch"
    ],

    "manufacturing_date": [
        "date of manufacture",
        "date of mfg",
        "date of manufacturing",
        "mfg date",
        "date o mg"
    ],

    "expiry_date": [
        "expiry date",
        "exp date",
        "use by",
        "use sy",
        "best before"
    ]
}


# ---------------------------------------------------------
# Basic text cleaning
# ---------------------------------------------------------

def clean_text(text):

    text = str(text)

    # Remove excessive spaces
    text = re.sub(r"\s+", " ", text)

    # Remove spaces around punctuation
    text = re.sub(r"\s+([:;,.-])", r"\1", text)

    return text.strip()


# ---------------------------------------------------------
# Similarity
# ---------------------------------------------------------

def similarity(a, b):

    return SequenceMatcher(
        None,
        a.lower(),
        b.lower()
    ).ratio()


# ---------------------------------------------------------
# Detect possible field
# ---------------------------------------------------------

def detect_field(text):

    cleaned = clean_text(text).lower()

    best_field = None
    best_score = 0

    for field, aliases in FIELD_ALIASES.items():

        for alias in aliases:

            score = similarity(
                cleaned,
                alias
            )

            if score > best_score:
                best_score = score
                best_field = field

    # Require reasonable similarity
    if best_score >= 0.70:

        return {
            "field": best_field,
            "confidence": round(best_score, 3),
            "original_text": text,
            "normalized_text": cleaned
        }

    return None


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    test_texts = [
        "MR",
        "Net Wight",
        "Bat No",
        "Date o Mg",
        "Use sy",
        "Random text"
    ]

    print("========== NORMALIZER TEST ==========")

    for text in test_texts:

        result = detect_field(text)

        print()
        print("OCR:", text)
        print("Result:", result)