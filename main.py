### --- main.py ---
import os
from pathlib import Path
from extractor.text_extractor import extract_text
from extractor.image_extractor import extract_images
from fallback.ocr_runner import run_ocr_if_needed
from fallback.ocr_merger import merge_ocr_results
from fallback.completeness_checker import check_completeness
from utils.markdown_writer import write_markdown

def process_pdf(pdf_path):
    output_dir = Path("output")
    images_dir = output_dir / "images"
    output_dir.mkdir(exist_ok=True)
    images_dir.mkdir(exist_ok=True)

    print("[*] Extracting text...")
    text_blocks, _ = extract_text(pdf_path)

    print("[*] Extracting images...")
    image_refs = extract_images(pdf_path, images_dir)

    print("[*] Checking completeness per page...")
    issues_by_page = check_completeness(pdf_path, text_blocks, image_refs)

    if issues_by_page:
        print("[!] Issues detected. Running OCR fallback on specific pages...")
        ocr_results = run_ocr_if_needed(pdf_path, issues_by_page)
        text_blocks = merge_ocr_results(text_blocks, ocr_results)

    print("[*] Writing to Markdown...")
    write_markdown(text_blocks, image_refs, output_dir / "markdown_output.md")
    print("[✓] Done. Markdown output saved to output/markdown_output.md")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_pdf>")
    else:
        process_pdf(sys.argv[1])