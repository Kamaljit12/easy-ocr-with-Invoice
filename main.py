from fastapi import FastAPI, UploadFile, File
from fastapi.responses import PlainTextResponse
from contextlib import asynccontextmanager
from ocr_engine import get_ocr_reader
from fastapi.responses import JSONResponse
from ll_model import extract_invoice_data
import os
import shutil
import logging


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


app = FastAPI(
    title="EasyOCR API",
    lifespan=lifespan
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/ocr_json")
async def ocr_json(file: UploadFile = File(...)):
    logger.info("📥 [START] Invoice processing started")
    logger.info(f"📄 Received file: {file.filename}")
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    logger.info("🔍 [OCR] OCR processing started")
    reader = get_ocr_reader()

    # EasyOCR inference
    results = reader.readtext(file_path)
    logger.info("✅ [OCR] OCR completed")

    os.remove(file_path)

    response = []
    for bbox, text, confidence in results:
        response.append({
            "text": text,
            "confidence": round(float(confidence), 4)
        })

    logger.info(f"📝 [OCR] Extracted")
    return {
        "filename": file.filename,
        "results": response
    }

@app.post("/ocr_get_text", response_class=PlainTextResponse)
async def ocr_get_text(file: UploadFile = File(...)):
    logger.info("📥 [START] Invoice processing started")
    logger.info(f"📄 Received file: {file.filename}")
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    logger.info("🔍 [OCR] OCR processing started")
    reader = get_ocr_reader()
    results = reader.readtext(file_path)
    logger.info("✅ [OCR] OCR completed")

    os.remove(file_path)

    # Extract only text
    texts = [text for _, text, _ in results]

    # Join lines nicely
    final_text = "\n".join(texts)
    logger.info(f"📝 [OCR] Extracted {len(final_text)} characters")
    return final_text


@app.post("/ocr_text_allined", response_class=PlainTextResponse)
async def ocr_text_allined(file: UploadFile = File(...)):
    logger.info("📥 [START] Invoice processing started")
    logger.info(f"📄 Received file: {file.filename}")
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    logger.info("🔍 [OCR] OCR processing started")
    reader = get_ocr_reader()
    results = reader.readtext(file_path)
    logger.info("✅ [OCR] OCR completed")

    os.remove(file_path)

    final_text = " ".join([text for _, text, _ in results])
    logger.info(f"📝 [OCR] Extracted {len(final_text)} characters")
    return final_text


# @app.post("/invoice-chatbot")
# async def invoice_chatbot(file: UploadFile = File(...)):
#     file_path = os.path.join(UPLOAD_DIR, file.filename)

#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     reader = get_ocr_reader()
#     results = reader.readtext(file_path)

#     os.remove(file_path)

#     ocr_text = " ".join([text for _, text, _ in results])

#     # LLM extraction
#     invoice_json = extract_invoice_data(ocr_text)

#     return invoice_json



@app.post("/invoice-chatbot")
async def invoice_chatbot(file: UploadFile = File(...)):
    logger.info("📥 [START] Invoice processing started")
    logger.info(f"📄 Received file: {file.filename}")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # ---------------- OCR ----------------
    logger.info("🔍 [OCR] OCR processing started")
    reader = get_ocr_reader()
    ocr_results = reader.readtext(file_path)
    logger.info("✅ [OCR] OCR completed")

    os.remove(file_path)

    ocr_text = "\n".join([text for _, text, _ in ocr_results])
    logger.info(f"📝 [OCR] Extracted {len(ocr_text)} characters")

    # ---------------- LLM ----------------
    logger.info("🧠 [LLM] Invoice extraction started (LLaMA-3)")
    invoice_json = extract_invoice_data(ocr_text)
    logger.info("✅ [LLM] Invoice extraction completed")

    logger.info("🏁 [DONE] Invoice processing completed successfully")

    return invoice_json



if __name__ == "__main__":
    import torch
    print("EasyOCR GPU enabled:", torch.cuda.is_available())

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=1,
        reload=False
    )
