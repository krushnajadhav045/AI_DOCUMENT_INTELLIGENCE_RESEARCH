import os
from google import genai
from google.genai import types


class GeminiService:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured"
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = "gemini-3.6-flash"

    def correct_ocr(
        self,
        image_path: str,
        ocr_text: str
    ):

        with open(image_path, "rb") as file:

            image_bytes = file.read()

        prompt = f"""
You are an expert document understanding system.

The OCR engine extracted the following text:

----------------
{ocr_text}
----------------

The OCR may contain errors caused by:
- noise
- skew
- handwriting
- low resolution
- similar characters
- broken characters
- table alignment

Analyze the supplied document image together with the OCR.

Correct only errors that are strongly supported by the image
and document context.

Do not invent information.

Return the corrected text while preserving the original meaning,
numbers, dates, names and document structure.
"""

        response = self.client.models.generate_content(

            model=self.model,

            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/png"
                ),
                prompt
            ]
        )

        return response.text