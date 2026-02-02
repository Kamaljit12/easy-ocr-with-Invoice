# Invoice OCR Automation

A FastAPI-based invoice processing system that uses Optical Character Recognition (OCR) and Large Language Models (LLM) to extract, validate, and manage invoice data with human-in-the-loop (HITL) capabilities.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Workflow Details](#workflow-details)
- [Module Documentation](#module-documentation)
- [Usage Examples](#usage-examples)
- [Directory Structure](#directory-structure)

---

## 🎯 Project Overview

Invoice OCR Automation is an intelligent document processing system designed to:

1. **Extract** invoice information from documents using OCR (EasyOCR)
2. **Process** extracted text through LLM-powered extraction pipelines
3. **Validate** extracted data against required fields
4. **Review** incomplete invoices with human intervention (HITL)
5. **Manage** invoice state through a stateful workflow graph

The system uses **LangGraph** for workflow orchestration and **Groq LLM** for intelligent extraction and validation.

---

## 🏗️ Architecture

### Technology Stack

- **Backend Framework**: FastAPI
- **OCR Engine**: EasyOCR (GPU-accelerated)
- **LLM Provider**: Groq (Llama 3.3 70B)
- **Workflow Engine**: LangGraph
- **Data Validation**: Pydantic
- **Language Model Framework**: LangChain

### Workflow Pipeline

```
Invoice Upload
     ↓
OCR Text Extraction
     ↓
LLM-based Field Extraction
     ↓
Confidence Scoring
     ↓
Validation
     ├─→ All fields present → Complete
     └─→ Missing fields → Human Review (HITL)
     ↓
Human Input Application
     ↓
Completion
```

---

## ✨ Features

- **GPU-Accelerated OCR**: Leverages CUDA for fast document scanning
- **Intelligent Field Extraction**: Uses Groq's Llama 3.3 70B model for semantic understanding
- **Confidence Scoring**: Tracks confidence levels for each extracted field
- **Missing Field Detection**: Automatically identifies incomplete invoices
- **Human-in-the-Loop**: Pauses workflow for human review when needed
- **State Management**: Thread-based stateful processing with memory persistence
- **Structured Output**: Type-safe Pydantic schemas for all data
- **JSON Persistence**: Stores OCR results and state snapshots for auditing

---

## 📦 Prerequisites

- **Python 3.8+**
- **CUDA 11.8** (for GPU acceleration with PyTorch)
- **Groq API Key** (obtain from [console.groq.com](https://console.groq.com))
- **4GB+ VRAM** (recommended for GPU acceleration)
- **8GB+ RAM** (minimum system RAM)

---

## 🚀 Installation

### 1. Clone or Navigate to Project

```bash
cd ocr_invoice_atomation/api
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/Scripts/activate  # Windows
# or
source venv/bin/activate  # Linux/macOS
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt --index-url https://pypi.org/simple
```

**Note**: The `--index-url` flag is used for PyTorch CUDA 11.8 wheels from the official PyTorch repository.

### 4. Set Environment Variables

Create a `.env` file in the api directory:

```env
GROQ_API_KEY=your_groq_api_key_here
```

---

## ⚙️ Configuration

### [config.py](config.py)

The `Config` class defines all application settings:

| Setting | Value | Description |
|---------|-------|-------------|
| `REQUIRED_FIELDS` | List of 5 fields | Fields that must be extracted: `invoice_id`, `invoice_date`, `due_date`, `amount`, `vendor_name` |
| `GROQ_API_KEY` | Environment variable | API key for Groq LLM access |
| `CONFIDENCE_THRESHOLD` | 0.7 | Minimum confidence score for field acceptance (0.0-1.0) |
| `USE_GPU` | True | Enable GPU acceleration for OCR |
| `USE_CPU` | False | Fallback CPU mode (set True to disable GPU) |
| `OCR_JSON_DIR` | `ocr_extracted_json/` | Directory for storing OCR results |

### LLM Extraction Prompt

The system uses a structured prompt template to ensure JSON-formatted output:

```
Task: Extract structured invoice information with confidence scores
Rules:
- Extract explicitly present values only
- Provide confidence between 0.0 and 1.0
- Return null for missing fields
- Do NOT guess values
- Output STRICT JSON
```

---

## 📡 API Endpoints

### 1. OCR Text Extraction

**POST** `/ocr_text_allined`

Uploads an invoice document and extracts raw text using EasyOCR.

**Request**:
- `file`: Invoice document (PDF, image, etc.)

**Response**:
```json
{
  "raw_text": "Invoice #INV-2024-001...",
  "thread_id": "uuid-string"
}
```

**Status Codes**: 200 (Success), 400 (Invalid file)

---

### 2. Process Invoice

**POST** `/invoice/process/{thread_id}`

Initiates the full invoice processing workflow for a given thread.

**Parameters**:
- `thread_id`: UUID from OCR extraction step

**Response**:
```json
{
  "raw_text": "...",
  "invoice_id": "INV-2024-001",
  "invoice_date": "2024-01-15",
  "due_date": "2024-02-15",
  "amount": "1500.00",
  "vendor_name": "Acme Corp",
  "confidence": {
    "invoice_id": 0.95,
    "invoice_date": 0.92,
    ...
  },
  "missing_fields": [],
  "status": "completed",
  "thread_id": "uuid-string"
}
```

**Status Codes**: 200 (Success), 404 (Thread not found)

---

### 3. Get Invoice State

**GET** `/invoice/{thread_id}`

Retrieves the current state of an invoice without advancing the workflow.

**Parameters**:
- `thread_id`: UUID identifying the invoice

**Response**: Current `InvoiceState` object

**Status Codes**: 200 (Success), 404 (Invoice not found)

---

### 4. Submit Human Input

**POST** `/invoice/{thread_id}/human-input`

Submits corrections or missing field values from human review.

**Parameters**:
- `thread_id`: UUID identifying the invoice

**Request Body**:
```json
{
  "invoice_id": "INV-2024-001",
  "invoice_date": "2024-01-15",
  "due_date": "2024-02-15",
  "amount": "1500.00",
  "vendor_name": "Acme Corp"
}
```

**Response**: Updated `InvoiceState` with status "processing"

**Status Codes**: 200 (Success), 404 (Invoice not found)

---

## 🔄 Workflow Details

### Workflow Stages

#### Stage 1: Extract
- **Module**: [services.py](services.py) → `extract_invoice_fields()`
- **Purpose**: Parse raw OCR text and extract structured fields
- **Output**: `InvoiceState` with extracted fields and confidence scores
- **LLM Model**: Groq Llama 3.3 70B with structured output

#### Stage 2: Confidence Filtering
- **Module**: [utils.py](utils.py) → `confidence_agent()`
- **Purpose**: Filter out low-confidence fields (below threshold)
- **Threshold**: 0.7 (configurable)
- **Action**: Sets fields below threshold to `None`

#### Stage 3: Validation
- **Module**: [utils.py](utils.py) → `validate_invoice()`
- **Purpose**: Check for missing required fields
- **Output**: Populates `missing_fields` list and updates `status`

#### Stage 4: Routing Decision
- **Module**: [utils.py](utils.py) → `route_after_validation()`
- **Decision Logic**:
  - If `missing_fields` exists → Route to Human Review
  - Otherwise → Complete workflow

#### Stage 5: Human Review (Conditional)
- **Module**: [utils.py](utils.py) → `human_review()`
- **Purpose**: Pause workflow and wait for human intervention
- **Status**: Sets status to "waiting_for_human"
- **Trigger**: Calls [apply_human.py](apply_human.py) when human input is submitted

---

## 📚 Module Documentation

### [main.py](main.py)

**Purpose**: FastAPI application entry point and route definitions

**Key Components**:

1. **Lifespan Context Manager**
   - Initializes EasyOCR model on startup
   - Performs cleanup on shutdown

2. **Routes**:
   - `POST /ocr_text_allined`: OCR extraction endpoint
   - `POST /invoice/process/{thread_id}`: Start workflow
   - `GET /invoice/{thread_id}`: Get current state
   - `POST /invoice/{thread_id}/human-input`: Submit human corrections

3. **Features**:
   - Thread-based state management using UUIDs
   - JSON file storage for OCR results
   - Automatic cleanup of upload directory
   - Comprehensive logging with timestamps

---

### [config.py](config.py)

**Purpose**: Centralized configuration management

**Exports**:

- `Config.REQUIRED_FIELDS`: List of mandatory invoice fields
- `Config.GROQ_API_KEY`: LLM API authentication
- `Config.PROMPT`: LangChain prompt template for extraction
- `Config.OCR_SYSTEM_PROMPT`: System instructions for JSON output
- `Config.CONFIDENCE_THRESHOLD`: Minimum acceptable confidence
- `Config.USE_GPU`: GPU acceleration toggle
- `Config.OCR_JSON_DIR`: Storage path for OCR results

---

### [schemas.py](schemas.py)

**Purpose**: Pydantic data models for type safety and validation

**Models**:

1. **InvoiceState** - Main state container
   - `raw_text`: Extracted OCR text
   - `invoice_id`, `invoice_date`, `due_date`, `amount`, `vendor_name`: Extracted fields
   - `confidence`: Dict mapping field names to confidence scores (0.0-1.0)
   - `missing_fields`: List of fields not successfully extracted
   - `status`: Processing status ("processing", "waiting_for_human", "completed")

2. **HuamnInput** - Human correction input (TypedDict)
   - Field: Optional values for each required field

3. **ProcessInvoiceRequest** - API request model
   - `raw_text`: Raw invoice text

4. **ProcessInvoiceResponse** - API response model
   - Extends `InvoiceState` with `thread_id`

5. **OCRResponse** - OCR endpoint response
   - `raw_text`: Extracted text
   - `thread_id`: Unique identifier

---

### [ocr_engine.py](ocr_engine.py)

**Purpose**: OCR initialization and management

**Functions**:

- `get_ocr_reader()`: Lazy-loads EasyOCR model with GPU support
  - One-time initialization (singleton pattern)
  - Supports English text extraction
  - Returns global reader instance for reuse

**Configuration**:
- Language: English only (`['en']`)
- GPU Mode: Enabled if CUDA available

---

### [services.py](services.py)

**Purpose**: LLM-based invoice field extraction

**Functions**:

- `extract_invoice_fields(state: InvoiceState) -> InvoiceState`
  - Initializes Groq LLM with API key
  - Applies structured output schema
  - Invokes extraction chain
  - Preserves original `raw_text`
  - Returns enriched state with extracted fields and confidence scores

**LLM Configuration**:
- Model: Llama 3.3 70B (Groq)
- Temperature: 0 (deterministic, no randomness)
- Output Format: Structured JSON matching `InvoiceState` schema

---

### [workflow.py](workflow.py)

**Purpose**: LangGraph workflow orchestration

**Components**:

1. **State Graph**
   - Uses `InvoiceState` as state container
   - Memory checkpointer for state persistence

2. **Nodes**:
   - `extract`: Calls `extract_invoice_fields()` from services
   - `confidence`: Calls `confidence_agent()` from utils
   - `validate`: Calls `validate_invoice()` from utils
   - `human_review`: Calls `human_review()` from utils

3. **Edges**:
   - `START → extract` (entry point)
   - `extract → confidence` (always)
   - `confidence → validate` (always)
   - `validate → {human_review, END}` (conditional routing)
   - `human_review → END` (HITL pause point)

4. **Memory Persistence**
   - `InMemorySaver` checkpointer for thread-based state management
   - Enables state retrieval and continuation

---

### [utils.py](utils.py)

**Purpose**: Utility functions for workflow and file management

**Functions**:

1. **`validate_invoice(state: InvoiceState) -> InvoiceState`**
   - Checks for missing required fields
   - Populates `missing_fields` list
   - Updates status: "waiting_for_human" if missing fields, else "completed"

2. **`route_after_validation(state: InvoiceState) -> str`**
   - Returns "human_review" if missing fields exist
   - Returns "end" if all fields present
   - Used for conditional edge routing

3. **`human_review(state: InvoiceState) -> InvoiceState`**
   - Sets status to "waiting_for_human"
   - Pauses workflow for human intervention
   - Returns unchanged state

4. **`confidence_agent(state: InvoiceState) -> InvoiceState`**
   - Iterates through required fields
   - Compares confidence scores against threshold
   - Nullifies fields below threshold
   - Returns filtered state

5. **`store_ocr_extracted_result(ocr_result: OCRResponse)`**
   - Creates `ocr_extracted_json/` directory if missing
   - Saves OCR result as JSON: `{thread_id}.json`
   - Enables result retrieval for processing

6. **`clear_ocr_dir()`**
   - Removes all files and directories in OCR storage
   - Used to clean up after processing

7. **`load_orc_extracted_json_file(dir_name: Path) -> List[Dict]`**
   - Reads all JSON files from OCR directory
   - Returns list of parsed JSON objects
   - Handles JSON decode errors gracefully

---

### [apply_human.py](apply_human.py)

**Purpose**: Human input application and state updates

**Functions**:

- `apply_human_input(state: Union[InvoiceState, Dict], human_data: Dict) -> InvoiceState`
  - Converts state to dictionary if needed
  - Extracts `missing_fields` list
  - Updates state with human-provided values
  - Removes updated fields from `missing_fields`
  - Resets status to "processing" to continue workflow
  - Returns updated `InvoiceState` object

**Workflow Integration**:
- Called when human submits corrections via `/invoice/{thread_id}/human-input`
- Allows field completion after LLM processing
- Re-initiates processing with complete data

---

### [ll_model.py](ll_model.py)

**Purpose**: Alternative LLM extraction pipeline (legacy/reference)

**Status**: Partially implemented, contains duplicate functionality

**Key Functions**:

- `safe_json_parse(text: str) -> dict`
  - Extracts JSON object from LLM response
  - Handles markdown code blocks and formatting
  - Includes retry logic for invalid responses

- `extract_invoice_data(ocr_text: str) -> dict`
  - Uses Groq LLM with system prompt
  - Implements single retry on parsing failure
  - Returns extracted invoice data as dictionary

**Note**: This module is superseded by [services.py](services.py) in the main workflow.

---

## 💡 Usage Examples

### Example 1: Full Invoice Processing Flow

```bash
# 1. Start FastAPI server
python main.py

# 2. Extract OCR text from invoice document
curl -X POST http://localhost:8000/ocr_text_allined \
  -F "file=@invoice.pdf"

# Response:
# {
#   "raw_text": "Invoice #INV-2024-001...",
#   "thread_id": "a1b2c3d4-..."
# }

# 3. Process invoice with workflow
curl -X POST http://localhost:8000/invoice/process/a1b2c3d4 \
  -H "Content-Type: application/json"

# 4. Check current state
curl -X GET http://localhost:8000/invoice/a1b2c3d4

# 5. If waiting for human input, submit corrections
curl -X POST http://localhost:8000/invoice/a1b2c3d4/human-input \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_id": "INV-2024-001",
    "invoice_date": "2024-01-15",
    "due_date": "2024-02-15",
    "amount": "1500.00",
    "vendor_name": "Acme Corp"
  }'
```

### Example 2: Python Integration

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Upload and extract
with open("invoice.pdf", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/ocr_text_allined",
        files={"file": f}
    )
    data = response.json()
    thread_id = data["thread_id"]

# Process invoice
response = requests.post(
    f"{BASE_URL}/invoice/process/{thread_id}"
)
result = response.json()
print(json.dumps(result, indent=2))

# Handle missing fields if needed
if result["missing_fields"]:
    corrections = {
        "invoice_id": "INV-2024-001",
        "invoice_date": "2024-01-15",
        "due_date": "2024-02-15",
        "amount": "1500.00",
        "vendor_name": "Acme Corp"
    }
    response = requests.post(
        f"{BASE_URL}/invoice/{thread_id}/human-input",
        json=corrections
    )
```

---

## 📁 Directory Structure

```
ocr_invoice_automation/
├── api/
│   ├── main.py                          # FastAPI entry point
│   ├── config.py                        # Configuration settings
│   ├── schemas.py                       # Pydantic data models
│   ├── ocr_engine.py                    # EasyOCR initialization
│   ├── services.py                      # LLM field extraction
│   ├── workflow.py                      # LangGraph workflow
│   ├── utils.py                         # Utility functions
│   ├── apply_human.py                   # Human input handling
│   ├── ll_model.py                      # Legacy LLM extraction
│   ├── requirements.txt                 # Python dependencies
│   ├── uploads/                         # Temporary file storage
│   └── ocr_extracted_json/              # OCR result persistence
│       └── {thread_id}.json             # Individual results
├── frontend/                            # Frontend application (TBD)
└── README.md                            # This file
```

---

## 🔧 Development & Debugging

### Logging

The application includes comprehensive logging:

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
```

Check logs for:
- OCR processing progress (`[OCR]` prefix)
- Invoice processing stages (`[START]`, `[EXTRACT]`)
- State transitions (`[VALIDATE]`, `[HUMAN_REVIEW]`)

### API Documentation

Once the server is running, visit:
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)

### Troubleshooting

| Issue | Solution |
|-------|----------|
| CUDA not found | Set `USE_GPU = False` in config.py |
| Groq API errors | Verify `GROQ_API_KEY` in .env file |
| Port 8000 in use | Change port in main.py uvicorn.run() |
| Memory errors | Reduce batch size or use CPU mode |
| JSON parsing errors | Check OCR text quality and format |

---

## 🚀 Performance Considerations

- **GPU Acceleration**: EasyOCR with CUDA provides 5-10x speedup
- **LLM Inference**: Groq offers fast responses (typically <1 second)
- **State Management**: In-memory persistence adequate for single-server deployments
- **Scalability**: Consider distributed checkpointer (Redis, PostgreSQL) for multi-instance production

---

## 📝 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | Latest | Web framework |
| uvicorn | Latest | ASGI server |
| pydantic | Latest | Data validation |
| easyocr | Latest | Optical character recognition |
| torch | 2.x (CUDA 11.8) | Deep learning backend |
| torchvision | 2.x | Computer vision utilities |
| pillow | Latest | Image processing |
| opencv-python | Latest | Image manipulation |
| langchain-core | Latest | LLM framework core |
| langchain-community | Latest | Community integrations |
| langchain_groq | Latest | Groq LLM integration |
| langgraph | Latest | Workflow orchestration |
| pdf2image | Latest | PDF processing |

---

## 📄 License

[Add license information here]

---

## ✉️ Support & Contact

For issues, questions, or contributions, please [contact information].

---

**Last Updated**: February 2, 2026
