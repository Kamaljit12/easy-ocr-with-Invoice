# from paddleocr import PaddleOCR

# ocr_model = None

# def get_ocr_model():
#     global ocr_model
#     if ocr_model is None:
#         print("Initializing PaddleOCR (one-time)...")
#         ocr_model = PaddleOCR(
#             lang="en",           # ✅ supported
#             use_angle_cls=True,   # ✅ supported
#         )
#     return ocr_model



import easyocr

reader = None

def get_ocr_reader():
    global reader
    if reader is None:
        print("Initializing EasyOCR (one-time)...")
        reader = easyocr.Reader(
            ['en'],        # languages
            gpu=True      # ✅ GPU mode (recommended on Windows)
        )
    return reader

