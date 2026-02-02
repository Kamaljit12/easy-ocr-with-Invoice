# config.py
from langchain_core.prompts import ChatPromptTemplate
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

class Config:
    REQUIRED_FIELDS = [
        "invoice_id",
        "invoice_date",
        "due_date",
        "amount",
        "vendor_name",
    ]

    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

    PROMPT = ChatPromptTemplate.from_template(
        """
        You are extracting structured invoice information.

        For EACH field:
        - Extract the value if explicitly present in the text
        - Provide a confidence score between 0.0 and 1.0
        - If the field is missing, return null and confidence 0.0
        - Do NOT guess values

        Return STRICT JSON matching the schema.

        Invoice text:
        {text}
        """)
    CONFIDENCE_THRESHOLD = 0.7

    # system prompt
    OCR_SYSTEM_PROMPT = """
        You are a JSON-only response engine.

        Task:
        Extract structured invoice information from OCR text.

        Rules (MANDATORY):
        - Output ONLY a valid JSON object.
        - Use double quotes for all keys and strings.
        - No markdown, no comments, no explanations.
        - No trailing commas.
        - If a value is missing, use null.
        - All numeric values must be floats.

        JSON schema:
        {
        "invoice_id": null,
        "vendor_name": null,
        "billing_date": null,
        "due_date": null,
        "currency": null,
        "line_items": [
            {
            "description": null,
            "quantity": null,
            "unit_price": null,
            "total_price": null
            }
        ],
        "subtotal": null,
        "tax_amount": null,
        "total_amount": null
        }
        """

    USE_GPU = True
    USE_CPU = False

    OCR_JSON_DIR = Path("ocr_extracted_json")