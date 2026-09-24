import json
from pathlib import Path

OCR_FILE = Path("backend/ocr_output/images (1)_res.json")

with OCR_FILE.open("r", encoding="utf-8") as file:
    data = json.load(file)

texts = data["rec_texts"]
boxes = data["rec_boxes"]

print()
print("========== OCR TEXT + COORDINATES ==========")
print()

for text, box in zip(texts, boxes):
    print(f"{text:<45}  BOX: {box}")

print()
print("Total OCR regions:", len(texts))