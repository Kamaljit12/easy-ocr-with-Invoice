import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    #  Groq configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    MODEL_NAME = "llama-3.1-8b-instant"
    TEMPERATURE = 0

    # system prompt
    SYSTEM_PROMPT = """
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



    GPU = True
    CPU = False

if __name__ == "__main__":
    print(Config().GROQ_API_KEY)