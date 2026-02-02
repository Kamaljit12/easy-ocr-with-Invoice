# schemas.py
from typing import Optional, Literal
from pydantic import BaseModel, Field
from typing import TypedDict

class InvoiceState(BaseModel):
    raw_text: Optional[str] = Field(
        None,
        description="Raw OCR or extracted text from the invoice document"
    )

    invoice_id: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    amount: Optional[str] = None
    vendor_name: Optional[str] = None

    confidence: dict[str, float] = Field(default_factory=dict)
    missing_fields: list[str] = Field(default_factory=list)
    status: Literal["processing", "waiting_for_human", "completed"] = "processing"

class HuamnInput(TypedDict):
    invoice_id: Optional[str]
    invoice_date: Optional[str]
    due_date: Optional[str]
    amount: Optional[str]
    vendor_name: Optional[str]

class ProcessInvoiceRequest(BaseModel):
    raw_text: str

class ProcessInvoiceResponse(InvoiceState):
    thread_id: str
    
class OCRResponse(BaseModel):
    raw_text: Optional[str]
    thread_id: Optional[str]