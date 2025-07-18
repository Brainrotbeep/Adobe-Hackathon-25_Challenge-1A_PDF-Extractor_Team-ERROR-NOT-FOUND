# PDF Heading Hierarchy Extractor

This project extracts the **document title** and **hierarchical headings (H1–H4)** from PDFs using layout, font, and pattern-based heuristics. It is fully containerized and runs on any system using Docker.

---

## 🧠 Approach

The extractor processes each PDF using:

### 1. **Text Extraction & Span Reconstruction**
- Extracts all text spans and metadata using **PyMuPDF** (`fitz`)
- Merges broken spans into full lines
- Captures font size, boldness, font name, y-position, and more

### 2. **Title Detection**
- Operates on the first page only
- Scores each candidate line using:
  - Font size and boldness
  - Proximity to top of page
  - Presence of “title” font family
  - Cleanliness of line (no numbering or artifacts)

### 3. **Heading Detection (H1–H4)**
- Uses a **hybrid rule-based approach** combining:
  - Font-size percentiles (e.g., top 10% → H1)
  - Bold formatting and visual positioning
  - Numbered heading patterns: `1.`, `1.1.1`, `A.`, `I.`, etc.
  - Multilingual script detection (Hindi, Japanese, Arabic, etc.)
  - ALL CAPS / Title Case heuristics
  - Keyword match: `Introduction`, `Background`, `Summary`, etc.

### 4. **Deduplication and Confidence Ranking**
- Normalizes text to remove duplicates and broken splits
- Assigns confidence scores and keeps only the strongest candidate per unique heading

---

## 🛠 How to Build and Run

### 🧱 Build the Docker Image

Run the following (as expected by the evaluation script):

```bash
docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .
```

### 🚀 Run the Docker Container

```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  mysolutionname:somerandomidentifier
```

This will:

- Read all `.pdf` files from `/app/input`
- Process each file to extract the title and headings
- Write a corresponding `.json` file into `/app/output`

For example:

```
input/
  └── E0H1CM114.pdf

output/
  └── E0H1CM114.json
```

---

## 📄 Output Format (`output.json`)

Each output file will contain:

```json
{
  "title": "Document Title",
  "outline": [
    { "level": "H1", "text": "Heading Level 1", "page": 1 },
    { "level": "H2", "text": "Subheading Level 2", "page": 2 },
    { "level": "H3", "text": "Minor Heading", "page": 3 }
  ]
}
```

This matches the evaluation specification exactly.

---

## 📚 Libraries Used

| Library   | Purpose                       |
|-----------|-------------------------------|
| `PyMuPDF` (`fitz`) | Text and layout extraction from PDF |
| `json`, `re`, `os` | Core Python libraries |
| `collections`, `math` | For scoring, sorting, and normalization |

---

## 🌐 Multilingual Support

✅ Hindi (Devanagari script)  
✅ Japanese (Hiragana, Katakana, Kanji)  
✅ Chinese, Arabic, Hebrew  
✅ Latin + Mixed-script documents

This is achieved by scanning for Unicode blocks in each heading line.

---

## 🧪 Tested Cases

- ✅ Structured brochures with clear headings
- ✅ Complex reports with non-standard fonts
- ✅ Multilingual documents with broken spans
- ✅ Edge cases with inconsistent formatting

> No machine learning — fast, explainable, robust.

---

## 📦 Deliverables

- `Dockerfile`: For containerization
- `app/main.py`: Main extraction script
- `/input`: Directory with input PDFs (mounted at runtime)
- `/output`: Directory for generated JSONs
- `README.md`: You are reading it ✅

---

## 🙌 Author

Built with love for the PDF Heading Extraction Hackathon 🏆