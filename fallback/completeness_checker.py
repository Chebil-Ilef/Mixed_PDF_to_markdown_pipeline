import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
import io

def check_completeness(pdf_path, extracted_text_blocks, image_refs):
    doc = fitz.open(pdf_path)
    issues_by_page = {}

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_issues = {"text": False, "images": False, "tables": False}

        # --- IMAGE CHECK ---
        expected_images = page.get_images(full=True)
        found = 0
        for img in expected_images:
            xref = str(img[0])
            if xref in image_refs:
                found += 1
        if found < len(expected_images):
            page_issues["images"] = True

        # --- TABLE CHECK (OpenCV line detection) ---
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("L")
        img_np = np.array(img)

        thresh = cv2.adaptiveThreshold(img_np, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                       cv2.THRESH_BINARY_INV, 15, 10)

        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        detected_lines = cv2.add(
            cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel),
            cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel)
        )

        contours, _ = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        possible_tables = [c for c in contours if cv2.contourArea(c) > 5000]  # filter small boxes

        table_found = len(possible_tables)
        markdown = extracted_text_blocks[page_num] if page_num < len(extracted_text_blocks) else ""
        if table_found > 0 and markdown.count("|") < table_found * 3:
            page_issues["tables"] = True

        # --- TEXT CHECK ---
        text_dict = page.get_text("dict")
        raw_text = " ".join(
            span["text"]
            for block in text_dict["blocks"] if block["type"] == 0
            for line in block["lines"]
            for span in line["spans"]
        ).strip()

        extracted_text = extracted_text_blocks[page_num] if page_num < len(extracted_text_blocks) else ""
        words_in_raw = set(raw_text.split())
        words_in_extracted = set(extracted_text.split())
        missing_words = words_in_raw - words_in_extracted

        if len(missing_words) / max(1, len(words_in_raw)) > 0.1:
            page_issues["text"] = True

        if any(page_issues.values()):
            issues_by_page[page_num] = page_issues

    return issues_by_page