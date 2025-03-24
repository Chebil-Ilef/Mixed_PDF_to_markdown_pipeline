import fitz

def check_completeness(pdf_path, text_blocks, tables, image_refs):
    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    text_ok = len(text_blocks) == total_pages
    image_count_estimate = sum(len(page.get_images(full=True)) for page in doc)
    image_ok = len(image_refs) >= image_count_estimate

    with doc:
        table_estimate = 0
        for page in doc:
            text = page.get_text("text")
            if any(sep in text for sep in ["|", "\t"]):
                table_estimate += 1

    table_ok = len(tables) >= table_estimate

    completeness = text_ok and image_ok and table_ok

    print(f"[Check] Text OK: {text_ok}, Images OK: {image_ok}, Tables OK: {table_ok}")
    return completeness