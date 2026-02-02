from langchain_groq import ChatGroq
from config import Config
from schemas import InvoiceState


def extract_invoice_fields(state: InvoiceState) -> InvoiceState:
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=Config.GROQ_API_KEY
    )

    structured_llm = llm.with_structured_output(InvoiceState)

    chain = Config.PROMPT | structured_llm

    result: InvoiceState = chain.invoke(
        {"text": state.raw_text}
    )

    # Preserve raw_text from original state
    result.raw_text = state.raw_text

    return result
