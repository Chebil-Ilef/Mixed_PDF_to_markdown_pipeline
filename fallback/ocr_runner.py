import fitz
import pytesseract
from PIL import Image
import io
import numpy as np
import cv2
import pandas as pd

def preprocess_for_ocr(img):
    """Enhance image contrast and binarize for better OCR accuracy."""
    img_np = np.array(img.convert("RGB"))
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    return Image.fromarray(thresh)

def extract_clean_ocr_text(pil_img, min_conf=60):
    """Run Tesseract OCR with confidence-based filtering and line reconstruction."""
    ocr_df = pytesseract.image_to_data(pil_img, lang="eng", output_type=pytesseract.Output.DATAFRAME)
    ocr_df = ocr_df.dropna()
    ocr_df = ocr_df[ocr_df["conf"].astype(int) >= min_conf]

    lines = []
    for _, group in ocr_df.groupby(['block_num', 'par_num', 'line_num']):
        line = " ".join(group['text'].tolist()).strip()
        if line:
            lines.append(line)
    return "\n".join(lines)

def run_ocr_if_needed(pdf_path, needs_ocr):
    doc = fitz.open(pdf_path)
    ocr_results = {}

    for page_num, info in needs_ocr.items():
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        pil_img = Image.open(io.BytesIO(pix.tobytes("png")))

        ocr_text = ""

        if info.get("missing_regions"):
            for region in info["missing_regions"]:
                x0, y0, x1, y1 = map(int, region["bbox"])
                region_crop = pil_img.crop((x0, y0, x1, y1))
                processed_crop = preprocess_for_ocr(region_crop)
                region_text = extract_clean_ocr_text(processed_crop)
                if region_text:
                    ocr_text += f"\n[OCR region] {region_text}"
        elif info.get("suspicious"):
            processed_full = preprocess_for_ocr(pil_img)
            full_text = extract_clean_ocr_text(processed_full)
            ocr_text += full_text

        ocr_results[page_num] = ocr_text.strip()

    return ocr_results
