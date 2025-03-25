import fitz
import pytesseract
from PIL import Image
import io

def run_ocr_if_needed(pdf_path, needs_ocr):
    doc = fitz.open(pdf_path)
    ocr_results = {}

    for page_num, info in needs_ocr.items():
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))

        ocr_text = ""
        if info.get("suspicious"):
            ocr_text += pytesseract.image_to_string(img)
        for region in info.get("missing_regions", []):
            x0, y0, x1, y1 = map(int, region["bbox"])
            region_crop = img.crop((x0, y0, x1, y1))
            ocr_text += "\n[OCR region] " + pytesseract.image_to_string(region_crop)

        ocr_results[page_num] = ocr_text.strip()

    return ocr_results
