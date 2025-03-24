import os
from extractor.text_extractor import extract_text
from extractor.image_extractor import extract_images
from extractor.completeness_checker import check_completeness
from fallback.ocr_handler import run_ocr_if_needed
from utils.markdown_writer import write_markdown

from pathlib import Path


def process_pdf(pdf_path):
    # Create output directories
    output_dir = Path("output")
    images_dir = output_dir / "images"
    output_dir.mkdir(exist_ok=True)
    images_dir.mkdir(exist_ok=True)

    print("[*] Extracting text...")
    text_blocks = extract_text(pdf_path)



    print("[*] Extracting images...")
    image_refs = extract_images(pdf_path, images_dir)

    # print("[*] Checking completeness...")

    print("[*] Writing to Markdown...")
    write_markdown(text_blocks, image_refs, output_dir / "markdown_output.md")

    print("[✓] Done. Markdown output saved to output/markdown_output.md")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_pdf>")
    else:
        process_pdf(sys.argv[1])
