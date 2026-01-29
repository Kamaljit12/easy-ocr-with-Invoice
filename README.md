# Easy-OCR Project

A comprehensive Optical Character Recognition (OCR) system that extracts text and structured data from invoices using EasyOCR and large language models (LLMs).

## 📋 Overview

This project combines EasyOCR for text extraction with FastAPI for serving and Groq LLMs for intelligent data extraction. It processes invoice images/PDFs and extracts structured information in JSON format.

## ✨ Features

- **OCR Processing**: Extract text from images and PDFs using EasyOCR
- **Invoice Data Extraction**: Automatically extract structured invoice information (vendor name, amount, dates, etc.)
- **FastAPI Server**: RESTful API endpoints for processing documents
- **JSON Output**: Structured data extraction with validation
- **Batch Processing**: Handle multiple documents
- **GPU Support**: Optimized for CUDA-enabled devices

## 📁 Project Structure

```
easy-ocr/
├── main.py                 # FastAPI application and API endpoints
├── ocr_engine.py          # EasyOCR wrapper and text extraction logic
├── ll_model.py            # LLM integration for data extraction
├── config.py              # Configuration and environment variables
├── requirements.txt       # Python dependencies
├── config.env             # Environment variables (Groq API key, etc.)
├── datasetes/             # Dataset directory
│   ├── documents/         # PDF and document files
│   └── images/            # Image files for OCR
├── uploads/               # Temporary storage for uploaded files
├── extracted.json         # Extracted invoice data (JSON format)
├── extracted.txt          # Extracted text output
```

## 🚀 Installation

### Prerequisites
- Python 3.8+
- CUDA 11.8 (recommended for GPU acceleration)
- Groq API Key

### Setup Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd easy-ocr
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the project root:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

## 🔧 Configuration

Edit `config.py` to customize:
- **GROQ_API_KEY**: Your Groq API key for LLM access
- **MODEL_NAME**: LLM model to use (default: "llama-3.1-8b-instant")
- **TEMPERATURE**: LLM response temperature (default: 0)
- **SYSTEM_PROMPT**: Customize the extraction instructions

## 📝 Usage

### Running the API Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

### API Endpoints

#### OCR and Extract Invoice Data (JSON)
**POST** `/ocr_json`

Upload an invoice image or PDF to extract structured data.

**Request:**
```bash
curl -X POST "http://localhost:8000/ocr_json" \
  -F "file=@invoice.png"
```

**Response:**
```json
{
  "invoice_id": "INV-2024-001",
  "vendor_name": "Company Name",
  "billing_date": "2024-01-15",
  "due_date": "2024-02-15",
  "total_amount": 1500.00,
  "items": [
    {
      "description": "Service",
      "quantity": 1,
      "unit_price": 1500.00,
      "total": 1500.00
    }
  ]
}
```

#### Extract OCR Text (Plain Text)
**POST** `/ocr_text`

Extract raw OCR text from the document.

**Request:**
```bash
curl -X POST "http://localhost:8000/ocr_text" \
  -F "file=@invoice.png"
```

### Using Locally

Process images directly from the `datasetes/images/` directory:

```python
from ocr_engine import get_ocr_reader
from ll_model import extract_invoice_data

# Get OCR reader
reader = get_ocr_reader()

# Read image
results = reader.readtext("path/to/image.png")
ocr_text = "\n".join([result[1] for result in results])

# Extract structured data
invoice_data = extract_invoice_data(ocr_text)
```

## 📦 Dependencies

- **torch, torchvision, torchaudio**: Deep learning framework with CUDA support
- **fastapi**: Modern web framework for building APIs
- **uvicorn**: ASGI server for FastAPI
- **easyocr**: OCR library
- **langchain**: LLM integration framework
- **groq**: Groq LLM API client
- **pillow, opencv-python**: Image processing
- **pdf2image**: PDF to image conversion

## 📊 File Descriptions

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application with API endpoints |
| `ocr_engine.py` | EasyOCR initialization and text extraction |
| `ll_model.py` | Groq LLM integration for data extraction |
| `config.py` | Configuration settings and prompts |
| `extracted.json` | Output file for extracted invoice data |
| `extracted.txt` | Output file for raw OCR text |

## 🔍 How It Works

1. **File Upload**: User uploads an invoice image/PDF via API
2. **OCR Processing**: EasyOCR extracts text from the image
3. **Data Extraction**: Groq LLM processes OCR text according to system prompt
4. **JSON Response**: Structured invoice data returned to user
5. **Storage**: Results saved to `extracted.json` and `extracted.txt`

## 🛠️ Troubleshooting

### OCR Model Not Loading
- Ensure CUDA is properly installed for GPU support
- Check disk space for model download (~200MB)
- Set `CUDA_VISIBLE_DEVICES=0` to specify GPU device

### API Not Starting
- Verify port 8000 is not in use
- Check all dependencies are installed: `pip install -r requirements.txt`
- Ensure Groq API key is set in `.env`

### LLM Extraction Failing
- Verify Groq API key is valid
- Check internet connection
- Review OCR output quality

## 📚 Resources

- [EasyOCR Documentation](https://github.com/JaidedAI/EasyOCR)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Groq API Documentation](https://console.groq.com/docs)
- [LangChain Documentation](https://python.langchain.com/)

## 📝 License

This project is provided as-is for educational and practical use.

## 🤝 Contributing

Contributions and improvements are welcome!

---

**Last Updated**: January 2026
