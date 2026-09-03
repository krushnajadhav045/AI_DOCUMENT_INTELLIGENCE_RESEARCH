import time
import json
import shutil
import re
import asyncio
from pathlib import Path

from config import UPLOAD_PATH, OUTPUT_PATH, TEMP_PATH, settings
from services.pdf_service import pdf_to_images
from services.excel_generator import create_excel
from services.json_export import export_json


def parse_invoice_text(text: str) -> dict:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return {}

    def get_next_line(label):
        for idx, l in enumerate(lines):
            if label.lower() in l.lower() and idx + 1 < len(lines):
                val = lines[idx + 1]
                if not any(k in val.lower() for k in ["description", "quantity", "unit price", "amount"]):
                    return val
        return None

    data = {}
    
    inv_no_match = re.search(r'INV-[\w-]+', text)
    if inv_no_match:
        data['invoice_number'] = inv_no_match.group(0)
    else:
        data['invoice_number'] = get_next_line('Invoice Number')

    data['invoice_date'] = get_next_line('Invoice Date')
    data['due_date'] = get_next_line('Due Date')
    
    if len(lines) > 1 and "INVOICE" in lines[0].upper():
        data['seller_name'] = lines[1]
    
    data['buyer_name'] = get_next_line('Customer')
    data['subtotal'] = get_next_line('Subtotal')

    tax_match = re.search(r'GST\s*\([^\)]+\)[\s:]*\n?([\d\,\.]+)', text, re.IGNORECASE)
    if tax_match:
        data['tax'] = tax_match.group(1)
    else:
        for idx, l in enumerate(lines):
            if ('gst (' in l.lower() or 'tax' in l.lower()) and idx + 1 < len(lines):
                data['tax'] = lines[idx + 1]
                break

    data['total'] = get_next_line('Grand Total') or get_next_line('Total')


    # Extract Line Items
    items = []
    try:
        desc_indices = [i for i, l in enumerate(lines) if 'description' in l.lower()]
        sub_indices = [i for i, l in enumerate(lines) if 'subtotal' in l.lower()]
        if desc_indices and sub_indices:
            start_i = desc_indices[0]
            end_i = sub_indices[0]
            item_lines = lines[start_i+1:end_i]
            item_lines = [l for l in item_lines if not any(h in l.lower() for h in ['quantity', 'unit price', 'amount'])]
            
            i = 0
            while i < len(item_lines):
                if i + 3 < len(item_lines) and (item_lines[i+1].isdigit() or item_lines[i+1].replace('.', '', 1).isdigit()):
                    try:
                        items.append({
                            'description': item_lines[i],
                            'quantity': float(item_lines[i+1]),
                            'unit_price': float(item_lines[i+2].replace(',', '')),
                            'amount': float(item_lines[i+3].replace(',', ''))
                        })
                        i += 4
                        continue
                    except Exception:
                        pass
                i += 1
    except Exception as e:
        print(f"Line item parsing warning: {e}")

    data['items'] = items
    return {k: v for k, v in data.items() if v is not None}


async def process_document(document_id: str) -> dict:
    start_time = time.time()

    # 1. Locate uploaded file
    doc_dir = UPLOAD_PATH / document_id
    target_file = None

    if doc_dir.exists() and doc_dir.is_dir():
        files = [f for f in doc_dir.iterdir() if f.is_file()]
        if files:
            target_file = files[0]

    if not target_file:
        for ext in [".pdf", ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"]:
            candidate = UPLOAD_PATH / f"{document_id}{ext}"
            if candidate.exists():
                target_file = candidate
                break
            candidate_orig = UPLOAD_PATH / "original" / f"{document_id}{ext}"
            if candidate_orig.exists():
                target_file = candidate_orig
                break

    if not target_file or not target_file.exists():
        raise FileNotFoundError(f"No document file found for ID: {document_id}")

    filename = target_file.name
    extension = target_file.suffix.lower()

    # Create processed directory for frontend preview and download
    processed_dir = OUTPUT_PATH / "ocr" / document_id / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    page_images = []
    extracted_text = ""

    if extension == ".pdf":
        try:
            page_images = await asyncio.to_thread(
                pdf_to_images, str(target_file), str(processed_dir)
            )
        except Exception as e:
            print(f"Error converting PDF to images: {e}")
            page_images = []

        # Instant native PDF text extraction — use blocks so table cells are on separate lines
        try:
            import pymupdf
            doc = pymupdf.open(str(target_file))
            page_texts = []
            for page in doc:
                # "blocks" mode returns one entry per paragraph/table-cell block
                blocks = page.get_text("blocks")  # list of (x0,y0,x1,y1,text,block_no,block_type)
                # Sort top-to-bottom, left-to-right so reading order is preserved
                blocks = sorted(blocks, key=lambda b: (round(b[1] / 10), b[0]))
                page_line = "\n".join(
                    blk[4].strip() for blk in blocks if blk[4].strip()
                )
                page_texts.append(page_line)
                extracted_text += page_line + "\n"
            doc.close()
        except Exception as err:
            print(f"PyMuPDF text extraction error: {err}")
            page_texts = []
    else:
        # Copy image file to processed directory
        dest_image = processed_dir / f"page_1{extension}"
        shutil.copy(str(target_file), str(dest_image))
        page_images = [str(dest_image)]

    # 2. Perform OCR Extraction if native text is absent/short
    ocr_results = []
    if not extracted_text or len(extracted_text.strip()) < 20:
        try:
            from services.ocr_service import OCRService
            ocr = OCRService()

            ocr_dir = OUTPUT_PATH / "ocr" / document_id / "ocr"
            ocr_dir.mkdir(parents=True, exist_ok=True)

            for idx, img_path in enumerate(page_images, start=1):
                res = await asyncio.to_thread(ocr.process, img_path, str(ocr_dir / f"page_{idx}"))
                ocr_results.append(res)
                if isinstance(res, dict) and "text" in res and res["text"]:
                    extracted_text += f"\n--- Page {idx} ---\n" + res["text"]
        except Exception as ocr_err:
            print(f"OCR Service exception: {ocr_err}")

    if not extracted_text:
        extracted_text = f"Document: {filename}"
        page_texts = [extracted_text]

    # Build per-page ocr_results if not already populated by OCR service
    if not ocr_results:
        if 'page_texts' in dir() and page_texts:
            ocr_results = [
                {"page": i + 1, "text": pt.strip()}
                for i, pt in enumerate(page_texts)
                if pt.strip()
            ]
        if not ocr_results:
            ocr_results = [{"page": 1, "text": extracted_text.strip()}]

    combined_text = extracted_text.strip()

    # 3. AI / Rule-based Structured Data Extraction
    structured_data = {}
    if settings.GEMINI_API_KEY:
        try:
            from services.structured_extraction import StructuredExtractor
            extractor = StructuredExtractor(settings.GEMINI_API_KEY)
            extracted_data = await asyncio.to_thread(extractor.extract_invoice, combined_text)
            structured_data = extracted_data.model_dump()
        except Exception as err:
            print(f"Gemini AI extraction fallback: {err}")

    rule_data = parse_invoice_text(combined_text)
    if rule_data:
        for k, v in rule_data.items():
            if not structured_data.get(k):
                structured_data[k] = v

    if not structured_data:
        structured_data = {
            "document_name": filename,
            "total_pages": len(page_images) or 1,
            "file_type": extension,
            "raw_text": combined_text[:500]
        }

    # 4. Save JSON result
    json_dir = OUTPUT_PATH / "ocr" / document_id / "json"
    json_dir.mkdir(parents=True, exist_ok=True)
    json_file = json_dir / "document_result.json"

    result_payload = {
        "document_id": document_id,
        "filename": filename,
        "pages": len(page_images) or 1,
        "processing_time_seconds": round(time.time() - start_time, 2),
        "structured_data": structured_data,
        "ocr_results": ocr_results,
        "full_text": combined_text
    }

    export_json(result_payload, str(json_file))

    main_json_dir = OUTPUT_PATH / "json"
    main_json_dir.mkdir(parents=True, exist_ok=True)
    export_json(result_payload, str(main_json_dir / f"{document_id}_result.json"))

    # 5. Generate Excel
    excel_dir = OUTPUT_PATH / "excel"
    await asyncio.to_thread(create_excel, document_id, result_payload, str(excel_dir))

    return result_payload