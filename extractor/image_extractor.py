import fitz  # PyMuPDF
import os


def extract_images(pdf_path, output_dir):
    doc = fitz.open(pdf_path)
    image_refs = {}

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        image_list = page.get_images(full=True)

        for img_idx, img_info in enumerate(image_list):
            xref = img_info[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            image_filename = f"page{page_num + 1}_img{img_idx + 1}.{image_ext}"
            image_path = os.path.join(output_dir, image_filename)

            with open(image_path, "wb") as f:
                f.write(image_bytes)

            image_refs[str(xref)] = f"![Image](./images/{image_filename})"

    return image_refs
