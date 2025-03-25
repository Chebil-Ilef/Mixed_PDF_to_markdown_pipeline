from difflib import SequenceMatcher
import re
import fitz
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
        missing_regions = []

        # --- IMAGE CHECK ---
        expected_images = page.get_images(full=True)
        found = 0
        for img in expected_images:
            xref = str(img[0])
            if xref in image_refs:
                found += 1
        if found < len(expected_images):
            page_issues["images"] = True

        # --- TABLE CHECK (OpenCV) ---
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
        possible_tables = [c for c in contours if cv2.contourArea(c) > 5000]

        markdown = extracted_text_blocks[page_num] if page_num < len(extracted_text_blocks) else ""
        markdown_tables = re.findall(r"\|(.+)\|", markdown)
        if len(possible_tables) > 0 and len(markdown_tables) < len(possible_tables):
            page_issues["tables"] = True
            for c in possible_tables:
                x, y, w, h = cv2.boundingRect(c)
                missing_regions.append({"bbox": [x, y, x + w, y + h]})

        # --- TEXT CHECK (fuzzy similarity) ---
        text_dict = page.get_text("dict")
        raw_text = " ".join(
            span["text"]
            for block in text_dict["blocks"] if block["type"] == 0
            for line in block["lines"]
            for span in line["spans"]
        ).strip()

        extracted_text = extracted_text_blocks[page_num] if page_num < len(extracted_text_blocks) else ""
        similarity = SequenceMatcher(None, raw_text, extracted_text).ratio()

        if similarity < 0.85:
            page_issues["text"] = True
            missing_regions.append({"bbox": [0, 0, page.rect.width, page.rect.height]})

        if any(page_issues.values()):
            issues_by_page[page_num] = {
                **page_issues,
                "suspicious": True,
                "missing_regions": missing_regions
            }

    return issues_by_page
