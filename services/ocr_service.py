import json
from pathlib import Path

try:
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None


_ocr_engine = None


def get_ocr_engine():
    global _ocr_engine
    if _ocr_engine is None:
        if PaddleOCR is None:
            print("WARNING: PaddleOCR package is not installed in the active environment.")
            return None
        print("=" * 60)
        print("INITIALIZING PADDLEOCR ENGINE")
        print("=" * 60)
        _ocr_engine = PaddleOCR(
            use_angle_cls=False,
            lang="en"
        )


        print("PADDLEOCR INITIALIZED SUCCESSFULLY")
    return _ocr_engine



class OCRService:

    def __init__(self):
        self.engine = get_ocr_engine()

    def process(
        self,
        image_path: str,
        output_dir: str
    ):
        output_dir = Path(output_dir)
        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        print(f"Processing OCR for: {image_path}")

        text_lines = []
        words = []

        if self.engine is None:
            return {"text": "", "lines": [], "words": []}

        try:
            ocr_result = self.engine.ocr(image_path, cls=True)

            if ocr_result and ocr_result[0]:
                for line in ocr_result[0]:
                    text = line[1][0]
                    confidence = round(float(line[1][1]), 4)
                    text_lines.append(text)
                    words.append({"text": text, "confidence": confidence})
        except Exception as e:
            print(f"PaddleOCR processing error: {e}")

        full_text = "\n".join(text_lines)

        res_data = {
            "text": full_text,
            "lines": text_lines,
            "words": words
        }

        # Save to output_dir for download endpoints
        try:
            with open(output_dir / "ocr_result.json", "w", encoding="utf-8") as f:
                json.dump(res_data, f, indent=2, ensure_ascii=False)

            with open(output_dir / "text.txt", "w", encoding="utf-8") as f:
                f.write(full_text)
        except Exception as err:
            print(f"Error saving OCR outputs: {err}")

        return res_data