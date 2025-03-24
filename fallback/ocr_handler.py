
import fitz
import pytesseract
from PIL import Image
import io

def run_ocr_if_needed(pdf_path):
    doc = fitz.open(pdf_path)
    ocr_text_blocks = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data))

        text = pytesseract.image_to_string(image)
        ocr_text_blocks.append(f"\n\n### OCR Page {page_num + 1}\n\n{text}\n")

    return ocr_text_blocks