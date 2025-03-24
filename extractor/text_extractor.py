import fitz  # PyMuPDF
import pdfplumber

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    plumber_pdf = pdfplumber.open(pdf_path)
    text_blocks = []
    image_positions = []

    for page_num, (page, plumber_page) in enumerate(zip(doc, plumber_pdf.pages)):
        items = []

        # Extract formatted text
        page_dict = page.get_text("dict")
        for block in page_dict["blocks"]:
            if block["type"] != 0:
                continue

            for line in block["lines"]:
                line_text_parts = []

                for span in line["spans"]:
                    text = span["text"].strip()
                    if not text or text.startswith("<image:"):
                        continue

                    font = span["font"]
                    size = span["size"]
                    color = span["color"]
                    hex_color = "#{:06x}".format(color)
                    is_bold = "Bold" in font or "bold" in font

                    raw_text = text
                    if is_bold:
                        raw_text = f"<strong>{raw_text}</strong>"
                    if hex_color != "#000000":
                        raw_text = f"<span style='color:{hex_color}'>{raw_text}</span>"

                    # Header formatting
                    if size > 18:
                        raw_text = f"# {raw_text}"
                    elif size > 15:
                        raw_text = f"## {raw_text}"

                    line_text_parts.append(raw_text)

                if line_text_parts:
                    line_combined = " ".join(line_text_parts)
                    bbox = block["bbox"]  # rough estimate
                    items.append(("text", float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3]), line_combined + "\n"))

        # Extract inline images
        image_info_list = page.get_image_info(xrefs=True)
        for img in image_info_list:
            xref = img["xref"]
            bbox = img["bbox"]
            if bbox:
                x0, y0, x1, y1 = bbox
                items.append(("image", float(x0), float(y0), float(x1), float(y1), str(xref)))
                image_positions.append((str(xref), page_num))

        # Extract tables with pdfplumber using better table settings
        tables = plumber_page.extract_tables({
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines",
            "intersection_tolerance": 5
        })

        for table in tables:
            if not table or not table[0]:
                continue

            # Reject if it's just 1 column or fewer than 2 rows (likely not a real table)
            if len(table[0]) < 2 or len(table) < 2:
                continue

            # Normalize and clean each row
            col_count = len(table[0])
            normalized_rows = []
            for row in table:
                if row is None:
                    continue
                clean_row = [(cell or "").strip() for cell in row]
                while len(clean_row) < col_count:
                    clean_row.append("")
                normalized_rows.append(clean_row)

            # Estimate Y position
            try:
                words = plumber_page.extract_words()
                y_top = float(words[0]['top']) if words else 0
            except:
                y_top = 0

            # Convert to Markdown table
            markdown_table = []

            # Try to attach the last nearby "Table ..." text block
            table_title = None
            for i in reversed(items):
                if i[0] == "text" and "table" in i[5].lower():
                    table_title = i[5]
                    break
            if table_title:
                markdown_table.append(f"**{table_title}**")

            markdown_table.append("| " + " | ".join(normalized_rows[0]) + " |")
            markdown_table.append("|" + "|".join("---" for _ in normalized_rows[0]) + "|")
            for row in normalized_rows[1:]:
                markdown_table.append("| " + " | ".join(row) + " |")

            table_text = "\n".join(markdown_table)
            items.append(("table", 0, y_top, 1000, y_top + 20, table_text))


        # Sort all content by top (y), then left (x)
        items_sorted = sorted(items, key=lambda i: (i[2], i[1]))

        # Compose final Markdown for this page
        page_content = [f"\n\n### Page {page_num + 1}\n\n"]
        for item in items_sorted:
            if item[0] == "text":
                page_content.append(item[5] + "\n")
            elif item[0] == "image":
                image_ref = f"[[IMAGE_{item[5]}]]"
                page_content.append(image_ref + "\n")
            elif item[0] == "table":
                page_content.append(item[5] + "\n")

        text_blocks.append("".join(page_content))

    plumber_pdf.close()
    return text_blocks
