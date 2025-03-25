# PDF to Markdown Extraction Pipeline

A modular and layout-aware PDF extraction system with region-based OCR fallback. Designed to convert complex PDFs—including scanned documents—into structured Markdown, preserving text, tables, and images.

---

## Features

- **Layout-preserving** Markdown output
- **Text, Table, and Image Extraction** using PyMuPDF and pdfplumber
- **Completeness Verification** with OpenCV and fuzzy similarity
- **Region-Aware OCR Fallback** using Tesseract
- **Smart Merging** of OCR results into original content flow
- Clean modular architecture for customization and extension

---

## Tech Stack

- `PyMuPDF` (fitz) – PDF layout and image extraction
- `pdfplumber` – Table detection and text structuring
- `Tesseract OCR` via `pytesseract` – Intelligent fallback for failed extractions
- `OpenCV` – Visual line detection for tables
- `PIL`, `difflib`, `Markdown` – Image processing, text matching, and formatting

---

## 📁 Structure

```bash
.
├── main.py                     # Entry point
├── README.md                   # Project overview and instructions
├── requirements.txt            # Python dependencies
├── extractor/
│   ├── text_extractor.py       # Core text, table, image extractor
│   └── image_extractor.py      # Handles xref image export
├── fallback/
│   ├── completeness_checker.py # Detects missing or incomplete content
│   ├── ocr_runner.py           # Region-based OCR engine
│   └── ocr_merger.py           # Merges fallback OCR results
├── utils/
│   └── markdown_writer.py      # Converts extracted blocks to Markdown
└── output/
    └── images/                 # Saved extracted images
```

---

## How to Run

```bash
python main.py path/to/your/input.pdf
```

Outputs:
- `output/markdown_output.md` – Final structured markdown
- `output/images/` – All extracted images


---

## License

MIT – use freely with attribution.
