import fitz  # PyMuPDF
import os
import json
import re
from collections import defaultdict, Counter

def clean_text(text):
    text = re.sub(r'\s+', ' ', text.strip())
    text = re.sub(r'^\d+\s*$', '', text)
    text = re.sub(r'^page\s+\d+\s*$', '', text, flags=re.IGNORECASE)
    return text.strip()

def extract_blocks(pdf_path):
    doc = fitz.open(pdf_path)
    blocks = []
    for page_num, page in enumerate(doc):
        for block in page.get_text("dict")["blocks"]:
            if "lines" not in block:
                continue
            combined_text = ""
            font_sizes = []
            font_flags = []
            fonts = []
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span.get("text", "").strip()
                    if not text:
                        continue
                    combined_text += text + " "
                    font_sizes.append(span["size"])
                    font_flags.append(span.get("flags", 0))
                    fonts.append(span.get("font", ""))
            if combined_text:
                blocks.append({
                    "text": clean_text(combined_text),
                    "font_size": max(font_sizes),
                    "avg_font_size": sum(font_sizes) / len(font_sizes),
                    "is_bold": any(f & (1 << 4) for f in font_flags),
                    "is_italic": any(f & (1 << 6) for f in font_flags),
                    "font_name": fonts[0] if fonts else "",
                    "y": block["bbox"][1],
                    "page": page_num
                })
    return blocks

def guess_title(blocks):
    candidates = [b for b in blocks if b["page"] == 0 and 10 < len(b["text"]) < 200]
    scored = []
    for b in candidates:
        score = 0
        if b["is_bold"]:
            score += 20
        if b["y"] < 200:
            score += 15
        if "title" in b["font_name"].lower():
            score += 15
        score += b["font_size"]
        scored.append((score, b["text"]))
    scored.sort(reverse=True)
    return scored[0][1] if scored else ""

def detect_heading_blocks(blocks):
    font_sizes = sorted({b["font_size"] for b in blocks}, reverse=True)
    levels = {}
    for i, size in enumerate(font_sizes):
        if i == 0:
            levels[size] = "H1"
        elif i == 1:
            levels[size] = "H2"
        else:
            levels[size] = "H3"

    heading_keywords = [
        'introduction', 'conclusion', 'summary', 'overview', 'abstract',
        'background', 'methodology', 'references', 'appendix', 'acknowledgement',
        'results', 'discussion', 'training', 'timeline', 'preface', 'bibliography'
    ]

    seen = set()
    headings = []
    for b in blocks:
        text = b["text"]
        if not text or text.lower() in seen:
            continue
        seen.add(text.lower())

        level = levels.get(b["font_size"], "H3")

        if text.isupper() and len(text) <= 80:
            level = "H1"
        elif b["is_bold"] and len(text) <= 100:
            level = "H2"
        elif any(k in text.lower() for k in heading_keywords):
            level = "H2"
        elif is_multilingual(text):
            level = "H2"

        headings.append({
            "level": level,
            "text": text,
            "page": b["page"]
        })
    return headings

def is_multilingual(text):
    return any((
        '\u0900' <= c <= '\u097F' or  # Devanagari (Hindi)
        '\u4e00' <= c <= '\u9fff' or  # CJK
        '\u3040' <= c <= '\u309f' or  # Hiragana
        '\u30a0' <= c <= '\u30ff'     # Katakana
    ) for c in text)

def main():
    input_dir = "/app/input"
    output_dir = "/app/output"
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if not filename.endswith(".pdf"):
            continue
        pdf_path = os.path.join(input_dir, filename)
        try:
            blocks = extract_blocks(pdf_path)
            title = guess_title(blocks)
            outline = detect_heading_blocks(blocks)

            output = {
                "title": title,
                "outline": outline
            }

            output_file = os.path.join(output_dir, filename.replace(".pdf", ".json"))
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)

            print(f"✅ Processed: {filename} -> {output_file}")
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")

if __name__ == "__main__":
    main()
