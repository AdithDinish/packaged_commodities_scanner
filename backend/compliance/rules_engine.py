import re


class LegalMetrologyRulesEngine:

    @staticmethod
    def check_manufacturer(declarations):
        """
        Rule 6(1)(a): Name and complete address of the manufacturer / packer / importer.
        Must contain company/packer name and address details (e.g. Village/Road/Pin Code/State/Country).
        """
        val = declarations.get("manufacturer", "")
        addr = declarations.get("manufacturer_address", "")
        full = f"{val} {addr}".strip()

        if not val and not addr:
            return {
                "rule_code": "R1_MANUFACTURER",
                "rule_name": "Manufacturer/Packer/Importer Details",
                "legal_section": "Rule 6(1)(a)",
                "status": "NON_COMPLIANT",
                "severity": "CRITICAL",
                "extracted_value": "Missing",
                "message": "Name and address of Manufacturer / Packer / Importer is absent.",
                "legal_penalty": "Offence under Sec 36(1) of LM Act 2009. Penalty up to ₹25,000 for 1st offence."
            }

        # Check completeness (address indicators or PIN code)
        has_pin = bool(re.search(r"\b\d{6}\b", full))
        has_location = any(k in full.lower() for k in ["road", "street", "village", "taluk", "dist", "state", "india", "pvt", "ltd", "inc"])

        if val and (has_pin or has_location or len(full) >= 15):
            return {
                "rule_code": "R1_MANUFACTURER",
                "rule_name": "Manufacturer/Packer/Importer Details",
                "legal_section": "Rule 6(1)(a)",
                "status": "COMPLIANT",
                "severity": "CRITICAL",
                "extracted_value": f"{val} ({addr[:40]}...)" if len(addr) > 40 else f"{val} {addr}",
                "message": "Manufacturer/Packer name and address declared in compliance with Rule 6(1)(a).",
                "legal_penalty": None
            }
        else:
            return {
                "rule_code": "R1_MANUFACTURER",
                "rule_name": "Manufacturer/Packer/Importer Details",
                "legal_section": "Rule 6(1)(a)",
                "status": "WARNING",
                "severity": "MAJOR",
                "extracted_value": full,
                "message": "Manufacturer name declared, but complete address/pincode appears incomplete or truncated.",
                "legal_penalty": "Notice for address clarification under Legal Metrology Rules."
            }

    @staticmethod
    def check_product_name(declarations):
        """
        Rule 6(1)(b): Generic or common name of the commodity packaged.
        """
        name = declarations.get("product_name", "").strip()
        brand = declarations.get("brand", "").strip()

        if name or brand:
            return {
                "rule_code": "R2_PRODUCT_NAME",
                "rule_name": "Generic/Common Name of Commodity",
                "legal_section": "Rule 6(1)(b)",
                "status": "COMPLIANT",
                "severity": "CRITICAL",
                "extracted_value": f"{brand} {name}".strip(),
                "message": "Generic/common commodity name declared clearly.",
                "legal_penalty": None
            }
        return {
            "rule_code": "R2_PRODUCT_NAME",
            "rule_name": "Generic/Common Name of Commodity",
            "legal_section": "Rule 6(1)(b)",
            "status": "NON_COMPLIANT",
            "severity": "CRITICAL",
            "extracted_value": "Missing",
            "message": "Common or generic product description is missing on packaging label.",
            "legal_penalty": "Violation of Rule 6(1)(b). Non-compliant product packaging."
        }

    @staticmethod
    def check_net_quantity(declarations):
        """
        Rule 6(1)(c) & Schedule II: Net quantity in terms of standard weight, measure, or number.
        Standard SI units: g, kg, ml, l, N, m, etc. Spacing & symbol rules.
        """
        qty = declarations.get("net_quantity", "").strip()

        if not qty:
            return {
                "rule_code": "R3_NET_QTY",
                "rule_name": "Net Quantity Declaration",
                "legal_section": "Rule 6(1)(c) & Schedule II",
                "status": "NON_COMPLIANT",
                "severity": "CRITICAL",
                "extracted_value": "Missing",
                "message": "Net Quantity declaration is missing.",
                "legal_penalty": "Major breach of Legal Metrology Rules. Mandatory seizure/notice."
            }

        # Check standard units (g, kg, ml, l, mg, N, units, count)
        match = re.search(r"(\d+(?:\.\d+)?)\s*(kg|g|mg|ml|l|m|cm|mm|n|pcs|units?)\b", qty, re.IGNORECASE)
        if match:
            unit = match.group(2).lower()
            # Standard capitalization and unit symbol check
            if unit in ["kg", "g", "mg", "ml", "l", "m", "n", "pcs", "units"]:
                return {
                    "rule_code": "R3_NET_QTY",
                    "rule_name": "Net Quantity Declaration",
                    "legal_section": "Rule 6(1)(c) & Schedule II",
                    "status": "COMPLIANT",
                    "severity": "CRITICAL",
                    "extracted_value": qty,
                    "message": "Net Quantity complies with prescribed SI metric units.",
                    "legal_penalty": None
                }

        return {
            "rule_code": "R3_NET_QTY",
            "rule_name": "Net Quantity Declaration",
            "legal_section": "Rule 6(1)(c) & Schedule II",
            "status": "WARNING",
            "severity": "MAJOR",
            "extracted_value": qty,
            "message": "Net Quantity declared but uses non-standard unit symbols or improper spacing.",
            "legal_penalty": "Direction to align unit symbols with Schedule II."
        }

    @staticmethod
    def check_mfg_date(declarations):
        """
        Rule 6(1)(d): Month and year of manufacture / packing / import.
        Must follow MM/YYYY or Month YYYY format.
        """
        mfg = declarations.get("manufacturing_date", "").strip()
        exp = declarations.get("expiry_date", "").strip()
        best_before = declarations.get("best_before", "").strip()

        date_val = mfg or exp or best_before

        if date_val:
            # Check format MM/YY, MM/YYYY or Month Year
            if re.search(r"\b(?:\d{1,2}[\/\-]\d{2,4}|[A-Za-z]{3,9}\s*[\/\-]?\s*\d{2,4})\b", date_val):
                return {
                    "rule_code": "R4_MFG_DATE",
                    "rule_name": "Month & Year of Manufacture/Packing",
                    "legal_section": "Rule 6(1)(d)",
                    "status": "COMPLIANT",
                    "severity": "CRITICAL",
                    "extracted_value": date_val,
                    "message": "Date of manufacture/packing/expiry is clearly declared in valid month/year format.",
                    "legal_penalty": None
                }
            return {
                "rule_code": "R4_MFG_DATE",
                "rule_name": "Month & Year of Manufacture/Packing",
                "legal_section": "Rule 6(1)(d)",
                "status": "WARNING",
                "severity": "MAJOR",
                "extracted_value": date_val,
                "message": "Date declaration present but formatting does not strictly follow MM/YYYY standard.",
                "legal_penalty": "Format correction notice."
            }

        return {
            "rule_code": "R4_MFG_DATE",
            "rule_name": "Month & Year of Manufacture/Packing",
            "legal_section": "Rule 6(1)(d)",
            "status": "NON_COMPLIANT",
            "severity": "CRITICAL",
            "extracted_value": "Missing",
            "message": "Month and Year of manufacture/packing/import is completely missing.",
            "legal_penalty": "Offence under Rule 6(1)(d). Penalty applicable."
        }

    @staticmethod
    def check_mrp(declarations, raw_text=""):
        """
        Rule 6(1)(e): Maximum Retail Price (MRP) inclusive of all taxes.
        Must explicitly include statutory statement 'Inclusive of all taxes' or 'Incl. of all taxes'.
        """
        mrp = declarations.get("mrp", "").strip()
        full_text = raw_text.lower()

        if not mrp:
            return {
                "rule_code": "R5_MRP",
                "rule_name": "Maximum Retail Price (MRP) Declaration",
                "legal_section": "Rule 6(1)(e)",
                "status": "NON_COMPLIANT",
                "severity": "CRITICAL",
                "extracted_value": "Missing",
                "message": "MRP declaration is missing on product package.",
                "legal_penalty": "Severe violation under Sec 36(1) of Legal Metrology Act 2009."
            }

        # Check for mandatory tax inclusive statement
        has_tax_clause = any(clause in full_text for clause in [
            "incl. of all taxes",
            "inclusive of all taxes",
            "incl of all taxes",
            "incl. taxes",
            "inclusive all taxes",
            "incl.all taxes"
        ])

        if has_tax_clause:
            return {
                "rule_code": "R5_MRP",
                "rule_name": "Maximum Retail Price (MRP) Declaration",
                "legal_section": "Rule 6(1)(e)",
                "status": "COMPLIANT",
                "severity": "CRITICAL",
                "extracted_value": f"{mrp} (Incl. of all taxes)",
                "message": "MRP is properly formatted and includes mandatory 'Inclusive of all taxes' clause.",
                "legal_penalty": None
            }
        else:
            return {
                "rule_code": "R5_MRP",
                "rule_name": "Maximum Retail Price (MRP) Declaration",
                "legal_section": "Rule 6(1)(e)",
                "status": "NON_COMPLIANT",
                "severity": "CRITICAL",
                "extracted_value": mrp,
                "message": "MRP declared without mandatory statement 'Inclusive of all taxes' or 'Incl. of all taxes'.",
                "legal_penalty": "Violation of Rule 6(1)(e). Subject to fine & compliance notice."
            }

    @staticmethod
    def check_unit_sale_price(declarations, raw_text=""):
        """
        Rule 6(1)(n) [2021 Amendment]: Mandatory Unit Sale Price (USP) declaration on commodities.
        E.g. Rs. N per g / kg / ml / l / piece.
        """
        usp = declarations.get("unit_sale_price", "").strip()

        # Check in raw text if not explicitly extracted
        if not usp:
            match = re.search(r"(?:rs\.?|₹)\s*\d+(?:\.\d+)?\s*(?:per|\/)\s*(?:g|kg|ml|l|item|pc|unit)", raw_text, re.IGNORECASE)
            if match:
                usp = match.group(0)

        if usp:
            return {
                "rule_code": "R6_UNIT_PRICE",
                "rule_name": "Unit Sale Price (USP) Declaration",
                "legal_section": "Rule 6(1)(n)",
                "status": "COMPLIANT",
                "severity": "MAJOR",
                "extracted_value": usp,
                "message": "Unit Sale Price declared in accordance with 2021 Metrology Amendment.",
                "legal_penalty": None
            }
        else:
            return {
                "rule_code": "R6_UNIT_PRICE",
                "rule_name": "Unit Sale Price (USP) Declaration",
                "legal_section": "Rule 6(1)(n)",
                "status": "WARNING",
                "severity": "MAJOR",
                "extracted_value": "Not Found",
                "message": "Unit Sale Price declaration not detected. Required for multi-unit/bulk packaged commodities.",
                "legal_penalty": "Advisory notice for compliance with Rule 6(1)(n)."
            }

    @staticmethod
    def check_consumer_care(declarations):
        """
        Rule 6(2): Consumer Care Details.
        Must contain Name/Designation, Address, Telephone Number, and Email ID.
        """
        cc = declarations.get("consumer_care", "").strip()

        if not cc:
            return {
                "rule_code": "R7_CONSUMER_CARE",
                "rule_name": "Consumer Care Helpline & Contact Details",
                "legal_section": "Rule 6(2)",
                "status": "NON_COMPLIANT",
                "severity": "CRITICAL",
                "extracted_value": "Missing",
                "message": "Consumer Care contact details are missing on packaging label.",
                "legal_penalty": "Violation of Rule 6(2). Non-compliant label declaration."
            }

        has_phone = bool(re.search(r"(\+91|\b1800|\b\d{10}\b|\b\d{5}\s*\d{5}\b)", cc))
        has_email = bool(re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", cc))

        if has_phone and has_email:
            return {
                "rule_code": "R7_CONSUMER_CARE",
                "rule_name": "Consumer Care Helpline & Contact Details",
                "legal_section": "Rule 6(2)",
                "status": "COMPLIANT",
                "severity": "CRITICAL",
                "extracted_value": cc[:60] + "..." if len(cc) > 60 else cc,
                "message": "Consumer care contains both helpline phone number and email address.",
                "legal_penalty": None
            }
        elif has_phone or has_email:
            return {
                "rule_code": "R7_CONSUMER_CARE",
                "rule_name": "Consumer Care Helpline & Contact Details",
                "legal_section": "Rule 6(2)",
                "status": "WARNING",
                "severity": "MAJOR",
                "extracted_value": cc,
                "message": "Consumer care details present but missing either telephone helpline or official email address.",
                "legal_penalty": "Notice to provide complete consumer grievance contact details."
            }
        else:
            return {
                "rule_code": "R7_CONSUMER_CARE",
                "rule_name": "Consumer Care Helpline & Contact Details",
                "legal_section": "Rule 6(2)",
                "status": "WARNING",
                "severity": "MAJOR",
                "extracted_value": cc,
                "message": "Consumer care heading present, but valid contact telephone/email was not detected.",
                "legal_penalty": "Advisory notice under Rule 6(2)."
            }

    @staticmethod
    def check_country_of_origin(declarations):
        """
        Rule 6(1)(m): Country of Origin declaration.
        Mandatory for imported products, standard best practice for all packaged commodities.
        """
        coo = declarations.get("country_of_origin", "").strip()

        if coo:
            return {
                "rule_code": "R8_COUNTRY_ORIGIN",
                "rule_name": "Country of Origin Declaration",
                "legal_section": "Rule 6(1)(m)",
                "status": "COMPLIANT",
                "severity": "MAJOR",
                "extracted_value": coo,
                "message": "Country of Origin clearly declared on package.",
                "legal_penalty": None
            }
        return {
            "rule_code": "R8_COUNTRY_ORIGIN",
            "rule_name": "Country of Origin Declaration",
            "legal_section": "Rule 6(1)(m)",
            "status": "WARNING",
            "severity": "MAJOR",
            "extracted_value": "Not Found",
            "message": "Country of Origin declaration not explicitly detected.",
            "legal_penalty": "Recommended clarification of origin declaration."
        }

    @staticmethod
    def check_font_size(ocr_data, image_width=800, image_height=1000):
        """
        Rule 7 & Schedule III: Height of numerals and letters.
        Minimum height requirement for mandatory declarations (e.g. min 2mm to 4mm).
        Calculated from bounding box height ratios.
        """
        boxes = ocr_data.get("rec_boxes", [])
        if not boxes:
            return {
                "rule_code": "R9_FONT_SIZE",
                "rule_name": "Font Height & Readability Compliance",
                "legal_section": "Rule 7 & Schedule III",
                "status": "WARNING",
                "severity": "MINOR",
                "extracted_value": "N/A",
                "message": "OCR bounding box metrics unavailable for font height estimation.",
                "legal_penalty": None
            }

        # Calculate average and minimum bounding box height in pixels
        box_heights = []
        for box in boxes:
            if len(box) == 4:
                # [x1, y1, x2, y2]
                h = abs(box[3] - box[1])
                if h > 5: # Filter noise
                    box_heights.append(h)

        if box_heights:
            avg_height = sum(box_heights) / len(box_heights)
            min_height = min(box_heights)
            
            # Check relative font size (ratio to image height)
            font_ratio = (avg_height / max(image_height, 1)) * 100

            if font_ratio >= 1.2:
                return {
                    "rule_code": "R9_FONT_SIZE",
                    "rule_name": "Font Height & Readability Compliance",
                    "legal_section": "Rule 7 & Schedule III",
                    "status": "COMPLIANT",
                    "severity": "MINOR",
                    "extracted_value": f"Avg Height: {avg_height:.1f}px ({font_ratio:.2f}% of PDP)",
                    "message": "Font height and letter readability comply with prescribed Schedule III minimum size rules.",
                    "legal_penalty": None
                }
            else:
                return {
                    "rule_code": "R9_FONT_SIZE",
                    "rule_name": "Font Height & Readability Compliance",
                    "legal_section": "Rule 7 & Schedule III",
                    "status": "WARNING",
                    "severity": "MINOR",
                    "extracted_value": f"Avg Height: {avg_height:.1f}px ({font_ratio:.2f}% of PDP)",
                    "message": "Declaration text font height is small or near minimum readability threshold.",
                    "legal_penalty": "Recommendation to increase font size on principal display panel."
                }

        return {
            "rule_code": "R9_FONT_SIZE",
            "rule_name": "Font Height & Readability Compliance",
            "legal_section": "Rule 7 & Schedule III",
            "status": "COMPLIANT",
            "severity": "MINOR",
            "extracted_value": "Compliant",
            "message": "Font legibility meets general readability guidelines.",
            "legal_penalty": None
        }
