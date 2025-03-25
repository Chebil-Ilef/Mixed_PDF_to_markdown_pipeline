def merge_ocr_results(text_blocks, ocr_results):
    for page_num, ocr_text in ocr_results.items():
        if page_num < len(text_blocks):
            if ocr_text not in text_blocks[page_num]:
                text_blocks[page_num] += f"\n\n[OCR fallback]\n{ocr_text}\n"
        else:
            text_blocks.append(f"\n\n[OCR fallback]\n{ocr_text}\n")
    return text_blocks
