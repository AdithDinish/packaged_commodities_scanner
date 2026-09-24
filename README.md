# 🏷️ Legal Metrology Packaged Commodities Scanner

An AI-powered computer vision and rule-evaluation system for automating packaged commodity label inspections under the **Legal Metrology Act, 2009** and **Legal Metrology (Packaged Commodities) Rules, 2011**, Government of India.

Designed for Enforcement Officials, Legal Metrology Inspectors, and Quality Auditors at the **Department of Consumer Affairs (DoCA)**, Ministry of Consumer Affairs, Food & Public Distribution.

---

## 🚀 Features

- **🔍 Automated Deep OCR Extraction**: Powered by PaddleOCR for high-precision text detection and 2D bounding box spatial mapping on complex packaging labels.
- **⚖️ 9-Point Mandatory Declaration Evaluator**: Evaluates label compliance across statutory requirements:
  1. **Manufacturer / Packer / Importer Details**: Full statutory address and business entity declaration.
  2. **Generic / Common Name**: Clear identification of packaged commodity.
  3. **Net Quantity & Units**: Standardized measurement unit validation (g, kg, ml, L, N).
  4. **Month & Year of Manufacture / Import**: Date format and legibility compliance.
  5. **Maximum Retail Price (MRP)**: Mandatory inclusion of *"incl. of all taxes"* or *"inclusive of all taxes"*.
  6. **Unit Sale Price (USP)**: Mandated per-gram / per-milliliter unit pricing assessment.
  7. **Consumer Care Details**: Helpline number, email, and address availability.
  8. **Country of Origin**: Mandatory origin statement for imported commodities.
  9. **Statutory Font Height**: Verification of text size compliance based on PDP (Principal Display Panel) area.
- **🎨 Interactive Bounding Box Inspection**: Visual overlay mapping extracted text regions with status colors:
  - 🟢 **Green (`#10B981`)**: Compliant Mandatory Declaration
  - 🔴 **Red (`#EF4444`)**: Non-Compliant / Statutory Violation
  - 🟡 **Amber (`#F59E0B`)**: Missing or Ambiguous Mandatory Field
- **📑 Official Digital Inspection PDF Report**: Automatic PDF report generation under Section 36 of the Legal Metrology Act, 2009, complete with officer sign-off fields, violation summary, and annotated packaging snapshots.
- **📊 Enforcement Analytics Dashboard**: High-level visual statistics tracking total inspections, compliance rates, and top statutory violations via Chart.js.
- **💾 Inspection Repository**: Built-in SQLite database powered by SQLAlchemy for indexing, searching, and managing past inspection records.

---

## 📂 Repository Structure

```
packaged_commodities_scanner/
├── backend/
│   ├── ai/                      # Text normalization, field detection & fuzzy matching
│   │   ├── field_detector.py
│   │   ├── text_normalizer.py
│   │   └── value_matcher.py
│   ├── compliance/              # Legal Metrology statutory rules engine
│   │   ├── evaluator.py
│   │   └── rules_engine.py
│   ├── database/                # SQLite DB setup & ORM models
│   │   ├── database.py
│   │   └── models.py
│   ├── routers/                 # FastAPI API endpoints
│   │   └── inspections.py
│   ├── services/                # OCR extraction & PDF report generator
│   │   ├── extraction_service.py
│   │   ├── ocr_service.py
│   │   └── report_generator.py
│   ├── tests/                   # Automated pytest suite
│   │   ├── test_api_scan.py
│   │   └── test_compliance.py
│   ├── main.py                  # FastAPI application entry point
│   ├── extractor.py
│   └── product_data.json
├── frontend/
│   └── index.html               # Modern dark-mode Single Page Application
├── PRODUCT.md                   # Product architecture & design principles
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn, SQLAlchemy, SQLite
- **Computer Vision & OCR**: PaddleOCR, OpenCV, Pillow (PIL)
- **PDF Generation**: ReportLab
- **Frontend**: HTML5, Vanilla JavaScript, CSS3 (Modern Slate Dark Theme with Glassmorphism)
- **Design & Typography**: Google Fonts (`Outfit` & `Inter`), Chart.js
- **Testing**: Pytest, HTTPX

---

## 💻 Quick Start

### 1. Prerequisites

- Python 3.10 or higher
- `pip` package manager

### 2. Clone Repository & Setup

```bash
git clone https://github.com/AdithDinish/packaged_commodities_scanner.git
cd packaged_commodities_scanner
```

### 3. Create & Activate Virtual Environment

```bash
# Windows
python -m venv backend/.venv
backend\.venv\Scripts\activate

# Linux / macOS
python3 -m venv backend/.venv
source backend/.venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Launch Application

```bash
python backend/main.py
```

The application will start at **`http://localhost:8000`**.

Open your browser and navigate to `http://localhost:8000` to access the Packaged Commodities Scanning Dashboard.

---

## 📡 API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/scan` | Upload packaging image, perform OCR & 9-point statutory compliance evaluation |
| `GET` | `/api/inspections` | Fetch list of historical inspection records |
| `GET` | `/api/inspections/{id}` | Get detailed inspection results and bounding box data for specific scan |
| `GET` | `/api/inspections/{id}/pdf` | Generate and download official DoCA PDF inspection report |
| `GET` | `/api/analytics` | Get enforcement analytics, pass/fail ratios, and violation breakdowns |

---

## 🧪 Running Tests

Run the unit and integration test suite with pytest:

```bash
pytest backend/tests
```

---

## ⚖️ Statutory Framework Reference

This software enforces rules established under:
1. **The Legal Metrology Act, 2009** (Act No. 1 of 2010), Section 36.
2. **The Legal Metrology (Packaged Commodities) Rules, 2011** (G.S.R. 427(E) & subsequent amendments).

---

## 📜 License

Developed for Department of Consumer Affairs enforcement and compliance auditing. All rights reserved.
