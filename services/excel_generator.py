from pathlib import Path
import json

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter


def create_excel(
    document_id: str,
    result: dict,
    output_directory: str
) -> str:

    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)

    excel_path = output_directory / f"{document_id}_result.xlsx"

    workbook = Workbook()
    
    header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")

    # ========================================================
    # SHEET 1 - DOCUMENT INFO
    # ========================================================
    sheet = workbook.active
    sheet.title = "Document Info"

    sheet.append(["Field", "Value"])
    sheet.append(["Document ID", document_id])
    sheet.append(["Filename", result.get("filename", "")])
    sheet.append(["Pages", result.get("pages", "")])
    sheet.append(["Processing Time (seconds)", result.get("processing_time_seconds", "")])

    # ========================================================
    # SHEET 2 - STRUCTURED DATA
    # ========================================================
    structured_sheet = workbook.create_sheet("Structured Data")
    structured_sheet.append(["Field", "Value"])

    structured_data = result.get("structured_data", {})
    items_list = []

    if isinstance(structured_data, dict):
        for key, value in structured_data.items():
            if key == "items" and isinstance(value, list):
                items_list = value
                continue

            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)

            structured_sheet.append([key, value])

    # ========================================================
    # SHEET 3 - LINE ITEMS (If present)
    # ========================================================
    if items_list:
        items_sheet = workbook.create_sheet("Line Items")
        items_sheet.append(["Description", "Quantity", "Unit Price", "Amount"])
        
        for item in items_list:
            if isinstance(item, dict):
                items_sheet.append([
                    item.get("description", ""),
                    item.get("quantity", ""),
                    item.get("unit_price", ""),
                    item.get("amount", "")
                ])

    # ========================================================
    # SHEET 4 - OCR TEXT (one row per line)
    # ========================================================
    ocr_sheet = workbook.create_sheet("OCR Text")
    ocr_sheet.append(["Page", "Line No.", "Extracted Text"])

    ocr_results = result.get("ocr_results", [])
    for page_index, ocr_res in enumerate(ocr_results, start=1):
        text_content = ""
        if isinstance(ocr_res, dict):
            text_content = ocr_res.get("text", "")
        elif isinstance(ocr_res, str):
            text_content = ocr_res
        else:
            text_content = json.dumps(ocr_res, ensure_ascii=False)

        # Split into individual lines — one row per line
        lines = [ln for ln in text_content.splitlines() if ln.strip()]
        if not lines:
            lines = [text_content]  # fallback: at least write something
        for line_no, line_text in enumerate(lines, start=1):
            ocr_sheet.append([page_index, line_no, line_text])

    # ========================================================
    # FORMAT STYLES & COLUMNS
    # ========================================================
    for current_sheet in workbook.worksheets:
        # Style header row
        for cell in current_sheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="left", vertical="center")

        for column in current_sheet.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)

            for cell in column:
                try:
                    val_str = str(cell.value or "")
                    if "\n" in val_str:
                        val_str = val_str.split("\n")[0]
                    max_length = max(max_length, len(val_str))
                except Exception:
                    pass

            current_sheet.column_dimensions[column_letter].width = min(max(max_length + 3, 12), 65)

    workbook.save(excel_path)
    return str(excel_path)