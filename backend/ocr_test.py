from paddleocr import PaddleOCR
from pathlib import Path

# Create OCR engine
ocr = PaddleOCR(
    lang="en",
    enable_mkldnn=False
)

# Product image
image_path = "backend/uploads/images (1).jpg"

# Run OCR
result = ocr.predict(image_path)

# Create output folder
output_folder = Path("backend/ocr_output")
output_folder.mkdir(parents=True, exist_ok=True)

# Save OCR result
for res in result:
    res.save_to_json(
        save_path=str(output_folder)
    )

print("OCR completed successfully!")
print("OCR JSON saved to:", output_folder)