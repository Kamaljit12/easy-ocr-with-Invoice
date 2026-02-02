# from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
import json
from langchain_groq import ChatGroq
from config import Config
import json
import re

# llm = ChatOllama(
#     model="llama3:latest",
#     temperature=0
# )

llm = ChatGroq(
    groq_proxy=Config.GROQ_API_KEY,
    temperature=Config.TEMPERATURE,
    model=Config.MODEL_NAME
)

def safe_json_parse(text: str) -> dict:
    """
    Safely extract JSON object from LLM output
    """
    # Grab the first JSON block
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON found in LLM output")

    json_str = match.group()

    # Remove newlines and extra spaces
    json_str = json_str.strip()

    return json.loads(json_str)


def extract_invoice_data(ocr_text: str) -> dict:
    messages = [
        SystemMessage(content=Config.OCR_SYSTEM_PROMPT),
        HumanMessage(content=f"OCR TEXT:\n{ocr_text}")
    ]

    response = llm.invoke(messages)

    try:
        return safe_json_parse(response.content)

    except Exception:
        # 🔁 Retry once with stronger instruction
        retry_messages = messages + [
            HumanMessage(
                content="Your previous response was invalid. "
                        "Return ONLY valid JSON matching the schema."
            )
        ]
        retry_response = llm.invoke(retry_messages)
        return safe_json_parse(retry_response.content)
