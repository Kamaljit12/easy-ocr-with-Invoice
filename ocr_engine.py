import easyocr
from config import Config
reader = None

def get_ocr_reader():
    global reader
    if reader is None:
        print("Initializing EasyOCR (one-time)...")
        reader = easyocr.Reader(
            ['en'],        # languages
            gpu=Config.USE_GPU      # ✅ GPU mode (recommended on Windows)
        )
    return reader

