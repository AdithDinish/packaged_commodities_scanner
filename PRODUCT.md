# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

FastAPI (Python backend), Vanilla HTML5/CSS3 & JavaScript (Frontend SPA), SQLite & SQLAlchemy (Persistence), PaddleOCR & PIL (Computer Vision), ReportLab (PDF Inspection Reports).

## Users

- **Primary Users**: Enforcement Officials, Legal Metrology Inspectors, and Quality Auditors at the Department of Consumer Affairs (DoCA), Ministry of Consumer Affairs, Food & Public Distribution, Govt. of India.
- **Situation & Job**: Conducting routine market inspections and compliance checking of retail packaged commodities (food, grocery, consumer goods, e-commerce listings) to detect non-compliant labels, missing mandatory declarations, improper MRP formatting, or non-standard font sizes under the Legal Metrology Act, 2009 and Legal Metrology (Packaged Commodities) Rules, 2011.

## Product Purpose

To automate the detection, extraction, and validation of mandatory packaging declarations using AI OCR and spatial rule evaluation, transforming manual, resource-intensive inspections into instant, digital, verifiable compliance assessments and legal notice reports.

## Positioning

First specialized legal metrology compliance scanning system in India featuring automated 9-point rule evaluation, 2D bounding box package label visual inspection, and instant official DoCA digital PDF report generation under Section 36 of the Legal Metrology Act, 2009.

## Operating Context

Field inspections in retail stores, market enforcement raids, warehouse quality audits, and e-commerce catalog monitoring. Inspectors upload package photographs, inspect annotated bounding boxes on display panels, verify extracted declarations, review score breakdown, and export signed digital inspection PDFs.

## Capabilities and Constraints

- **Confirmed Functionality**: 
  - Image upload & PaddleOCR scanning
  - 9 Mandatory Declaration Rules evaluation (Manufacturer, Common Name, Net Quantity, Mfg/Import Date, MRP with 'Incl. of all taxes', Unit Sale Price, Consumer Care Phone/Email, Country of Origin, Font Size/Height)
  - Color-coded bounding box annotation overlays (`#10B981` Green, `#EF4444` Red, `#F59E0B` Yellow)
  - Official DoCA Digital PDF Compliance Inspection Report generation
  - Scanned product repository & search database
  - Enforcement Analytics Dashboard (Chart.js charts for compliance breakdown and top violations)
- **Technical Constraints**: Compliance rules strictly mapped to Legal Metrology (Packaged Commodities) Rules, 2011 and Section 36 of Legal Metrology Act, 2009.

## Brand Commitments

- **Official Authority**: Department of Consumer Affairs (DoCA), Ministry of Consumer Affairs, Food & Public Distribution, Govt. of India.
- **Color Identity**: Slate dark background (`#0B0F19`, `#172036`), Sky Blue (`#38BDF8`), Emerald Green (`#10B981`), Amber (`#F59E0B`), Crimson (`#EF4444`).
- **Typography**: Google Fonts `Outfit` (headings) & `Inter` (body).

## Evidence on Hand

- Sample product packaging test image (`backend/uploads/test_sample.jpg`).
- Benchmark OCR JSON logs (`backend/ocr_output/images (1)_res.json`).
- Pre-packaged product metadata (`backend/product_data.json`).
- Automated pytest suite (`backend/tests/test_compliance.py`, `backend/tests/test_api_scan.py`).

## Product Principles

1. **Uncompromising Statutory Precision**: Rules strictly follow Legal Metrology 2011 specifications without generic fallbacks.
2. **Visual Inspection Clarity**: Direct color-coded bounding box overlays allow officers to visually correlate package text with compliance results.
3. **Audit Readiness**: Every scan creates an indelible inspection database record and a downloadable official PDF compliance report.
4. **Intuitive Officer UX**: Frictionless, single-click scanning and analytics dashboards designed for enforcement field productivity.
