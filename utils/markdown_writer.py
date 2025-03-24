
def write_markdown(text_blocks, image_refs, output_path):
    with open(output_path, "w", encoding="utf-8", errors="replace") as f:
        f.write("# Extracted PDF Content\n")

        for block in text_blocks:
            for line in block.splitlines():
                if line.strip().startswith("[[IMAGE_") and "]" in line:
                    xref = line.split("_", 1)[-1].strip("]")
                    f.write(image_refs.get(xref, "[Missing image]") + "\n")
                else:
                    f.write(line + "\n")
