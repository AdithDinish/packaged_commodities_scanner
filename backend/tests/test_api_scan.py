import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent
sys.path.append(str(BACKEND_DIR))

from fastapi.testclient import TestClient
from database.database import init_db
from main import app

init_db()
client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200

def test_api_scan_workflow():
    sample_img = BACKEND_DIR / "uploads" / "test_sample.jpg"
    sample_img.parent.mkdir(parents=True, exist_ok=True)
    
    # Create a small valid test image file
    from PIL import Image
    img = Image.new('RGB', (800, 1000), color=(240, 240, 240))
    img.save(sample_img)

    with sample_img.open("rb") as f:
        response = client.post("/api/scan?inspector_name=TestInspector", files={"file": ("test_sample.jpg", f, "image/jpeg")})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "scan_ref" in data
    assert "compliance_score" in data
    assert "report_url" in data
    assert len(data["rules_evaluation"]) == 9
    print("\nAPI Scan Test Successful! Scan Ref:", data["scan_ref"], "Score:", data["compliance_score"])

if __name__ == "__main__":
    test_api_scan_workflow()
