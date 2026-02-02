from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import PlainTextResponse
from contextlib import asynccontextmanager
from ocr_engine import get_ocr_reader
from fastapi.responses import JSONResponse
import os
from config import Config
import shutil
import logging
from schemas import (InvoiceState,
                     HuamnInput,
                     ProcessInvoiceRequest,
                     ProcessInvoiceResponse,
                     OCRResponse)
from workflow import get_workflow
from utils import (validate_invoice,
                   store_ocr_extracted_result,
                   load_orc_extracted_json_file,
                   clear_ocr_dir)
from apply_human import apply_human_input  # or wherever you defined it


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    get_ocr_reader()
    print("EasyOCR model loaded successfully")
    yield
    # Shutdown (optional cleanup)
    print("Shutting down...")

app = FastAPI(title="Invoice OCR Automation")

# Upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Compile workflow once
invoice_graph = get_workflow()


# ========================== OCR ==========================

@app.post("/ocr_text_allined", response_model=OCRResponse)
async def ocr_text_allined(file: UploadFile = File(...)):
    logger.info("📥 [START] Invoice processing started")
    logger.info(f"📄 Received file: {file.filename}")
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    # thread id
    thread_id = str(uuid.uuid4())

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    logger.info("🔍 [OCR] OCR processing started")
    reader = get_ocr_reader()
    results = reader.readtext(file_path)
    logger.info("✅ [OCR] OCR completed")

    os.remove(file_path)

    final_text = " ".join([text for _, text, _ in results])
    logger.info(f"📝 [OCR] Extracted {len(final_text)} characters")

    print("------------Clear OCR Dir------------------")
    if Config.OCR_JSON_DIR:
        clear_ocr_dir()
    else:
        pass
    print("------------OCR Dir has cleared---------------")

    store_ocr_extracted_result(OCRResponse(raw_text=final_text, thread_id=thread_id))
    print(f"OCR Extracted data has been stored in json file to {Config.OCR_JSON_DIR}")

    return OCRResponse(raw_text=final_text, thread_id=thread_id)


# -----------------------------
# 1️⃣ Start invoice processing
# -----------------------------
@app.post("/invoice/process/{thread_id}", response_model=InvoiceState)
def process_invoice(thread_id: str):

    loaded_json = load_orc_extracted_json_file(dir_name=Config.OCR_JSON_DIR)
    if loaded_json[0]["thread_id"] == thread_id:
        raw_text = loaded_json[0]['raw_text']

    result = invoice_graph.invoke(
        {"raw_text": raw_text},
        config={"configurable": {"thread_id": thread_id}}
    )

    return ProcessInvoiceResponse(
        **result,
        thread_id=thread_id
    )

# ----------------------------- 
# 2️⃣ Get current invoice state
# -----------------------------
@app.get("/invoice/{thread_id}", response_model=InvoiceState)
def get_invoice_state(thread_id: str):

    state = invoice_graph.get_state(
        config={"configurable": {"thread_id": thread_id}}
    )

    if not state:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return state.values


# -----------------------------
# 3️⃣ Submit human input
# -----------------------------
@app.post("/invoice/{thread_id}/human-input", response_model=InvoiceState)
def submit_human_input(thread_id: str, human_input: HuamnInput):

    # Load previous state
    state_snapshot = invoice_graph.get_state(
        config={"configurable": {"thread_id": thread_id}}
    )

    if not state_snapshot:
        raise HTTPException(status_code=404, detail="Invoice not found")

    current_state = state_snapshot.values

    # Apply human input
    updated_result = apply_human_input(
        state=current_state,
        human_data=human_input
    )

    return updated_result


if __name__ == "__main__":
    import uvicorn
    import torch
    print("EasyOCR GPU enabled:", torch.cuda.is_available())
    print("Starting API server on http://0.0.0.0:8000")
    print("To get api documentation, visit http://localhost:8000/docs")   
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)