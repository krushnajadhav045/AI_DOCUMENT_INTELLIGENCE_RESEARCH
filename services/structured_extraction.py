from google import genai
from google.genai import types

from models.document_models import InvoiceData


class StructuredExtractor:

    def __init__(self, api_key: str):

        self.client = genai.Client(
            api_key=api_key
        )

    def extract_invoice(self, text: str):

        prompt = f"""
Extract invoice information from the document text.

Rules:

1. Do not invent values.
2. Use null when information is missing.
3. Preserve invoice numbers exactly.
4. Preserve dates.
5. Extract every line item.
6. Calculate nothing unless the document explicitly provides it.
7. Return only structured data.

DOCUMENT:

{text}
"""

        response = self.client.models.generate_content(

            model="gemini-3.6-flash",

            contents=prompt,

            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=InvoiceData
            )
        )

        return InvoiceData.model_validate_json(
            response.text
        )