# utils.py
from config import Config
from schemas import InvoiceState, OCRResponse
from pathlib import Path
from config import Config
import json


def validate_invoice(state: InvoiceState) -> InvoiceState:

    state.missing_fields = [
        field 
        for field in Config.REQUIRED_FIELDS 
        if getattr(state, field) is None
        ]

    state.status = (
        "waiting_for_human" 
        if state.missing_fields 
        else "completed")
    
    return state


def route_after_validation(state: InvoiceState) -> str:
    if state.status == "waiting_for_human":
        return "human_review"
    return "end"


# Return entire state value for human review
def human_review(state: InvoiceState) -> InvoiceState:
    state.status = "waiting_for_human"
    return state

def route_on_start(state: InvoiceState) -> str:
    return "extract"

def confidence_agent(state: InvoiceState) -> InvoiceState:
    target_keys = [
        "invoice_id",
        "invoice_date",
        "due_date",
        "amount",
        "vendor_name",
    ]

    for key in target_keys:
        score = state.confidence.get(key, 0.0)
        if score < Config.CONFIDENCE_THRESHOLD:
            setattr(state, key, None)

    return state


def store_ocr_extracted_result(ocr_result: OCRResponse):
    Config.OCR_JSON_DIR.mkdir(exist_ok=True)
    if not Config.OCR_JSON_DIR.exists():
        Config.OCR_JSON_DIR.mkdir(parents=True)
    # Save extracted raw text into json with thread id
    with open(Config.OCR_JSON_DIR / f"{ocr_result.thread_id}.json", "w") as f:
        json.dump(dict(ocr_result), f, indent=2)


def clear_ocr_dir():
    if Config.OCR_JSON_DIR.is_dir():
        print(f"Dir exist: {Config.OCR_JSON_DIR}")
        for item in Config.OCR_JSON_DIR.iterdir():
            if item.is_file:
                item.unlink()
                print(f"File removed: {item}")
            elif item.is_dir():
                import shutil
                shutil.rmtree(item)

        print(f"Cleared directory: {Config.OCR_JSON_DIR}")
    else:
        print("Directory does not exist")


def load_orc_extracted_json_file(dir_name: Path):

    results = []
    if not dir_name.is_dir():
        raise FileNotFoundError(f"Directory not found: {dir_name}")

    for item in dir_name.iterdir():

        if item.is_file() and item.suffix.lower() == ".json":
            try:
                with item.open("r", encoding="utf-8") as f:
                    results.append(json.load(f))
            except json.JSONDecodeError as e:
                print(f"Invalid JSON in {item.name}: {e}")

    if not results:
        print("No JSON files found in OCR directory")

    return results