"""
FastAPI application for bib_checker with visual interface.
"""

import zipfile
import re
import os
import tempfile
import shutil
from io import TextIOWrapper
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI(title="Bib Checker", description="Visual tool to clean LaTeX bibliography")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def extract_citations(tex_content: str) -> set:
    """Extract all citation keys from .tex files."""
    pattern = re.compile(r'\\cite\w*\{([^}]+)\}')
    citations = set()
    for match in pattern.findall(tex_content):
        for key in match.split(','):
            citations.add(key.strip())
    return citations


def extract_bib_entries(bib_content: str) -> dict:
    """Extract entries from .bib and organize them in a dictionary."""
    entries = {}
    current_key = None
    current_entry = []
    inside_entry = False

    for line in bib_content.splitlines():
        if line.strip().startswith('@'):
            if current_key:
                entries[current_key] = '\n'.join(current_entry)
            current_entry = [line]
            inside_entry = True
            key_match = re.match(r'@\w+\{([^,]+),', line)
            current_key = key_match.group(1).strip() if key_match else None
        elif inside_entry:
            current_entry.append(line)

    if current_key:
        entries[current_key] = '\n'.join(current_entry)

    return entries


def parse_bib_entry(entry_text: str) -> dict:
    """Parse a .bib entry to extract key fields."""
    info = {
        "type": "unknown",
        "key": "",
        "title": "",
        "author": "",
        "year": "",
        "raw": entry_text
    }

    type_match = re.match(r'@(\w+)\{([^,]+),', entry_text.strip())
    if type_match:
        info["type"] = type_match.group(1)
        info["key"] = type_match.group(2).strip()

    title_match = re.search(r'title\s*=\s*[{"]([^}"]+)[}"]', entry_text, re.IGNORECASE)
    if title_match:
        info["title"] = title_match.group(1).strip()

    author_match = re.search(r'author\s*=\s*[{"]([^}"]+)[}"]', entry_text, re.IGNORECASE)
    if author_match:
        info["author"] = author_match.group(1).strip()

    year_match = re.search(r'year\s*=\s*[{"]?(\d{4})[}"]?', entry_text, re.IGNORECASE)
    if year_match:
        info["year"] = year_match.group(1)

    return info


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main page."""
    html_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return HTMLResponse("<h1>Bib Checker</h1><p>Place the index.html file in the static/ folder</p>")


@app.post("/api/upload")
async def upload_and_process(file: UploadFile = File(...)):
    """Process a ZIP file and return the analysis."""
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="File must be a ZIP")

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, file.filename)

    try:
        content = await file.read()
        with open(zip_path, "wb") as f:
            f.write(content)

        with zipfile.ZipFile(zip_path, 'r') as z:
            tex_files = [f for f in z.namelist() if f.endswith('.tex')]
            bib_files = [f for f in z.namelist() if f.endswith('.bib')]

            if not bib_files:
                raise HTTPException(status_code=400, detail="No .bib file found in ZIP")
            if not tex_files:
                raise HTTPException(status_code=400, detail="No .tex file found in ZIP")

            all_tex = ''
            for tex_file in tex_files:
                try:
                    with z.open(tex_file) as f:
                        all_tex += TextIOWrapper(f, encoding='utf-8').read()
                except UnicodeDecodeError:
                    raise HTTPException(status_code=400, detail=f"File {tex_file} is not UTF-8 encoded")

            cited_keys = extract_citations(all_tex)

            try:
                with z.open(bib_files[0]) as f:
                    bib_content = TextIOWrapper(f, encoding='utf-8').read()
            except UnicodeDecodeError:
                raise HTTPException(status_code=400, detail=f"File {bib_files[0]} is not UTF-8 encoded")

            all_entries = extract_bib_entries(bib_content)

            used_entries = {k: v for k, v in all_entries.items() if k in cited_keys}
            removed_entries = {k: v for k, v in all_entries.items() if k not in cited_keys}

            cited_parsed = [parse_bib_entry(v) for v in used_entries.values()]
            removed_parsed = [parse_bib_entry(v) for v in removed_entries.values()]

            return {
                "success": True,
                "filename": file.filename,
                "tex_files": tex_files,
                "bib_files": bib_files,
                "total_entries": len(all_entries),
                "cited_count": len(used_entries),
                "removed_count": len(removed_entries),
                "cited_keys": sorted(cited_keys),
                "cited_entries": cited_parsed,
                "removed_entries": removed_parsed,
            }

    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="File is not a valid ZIP")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@app.get("/api/download/{file_type}")
async def download_file(file_type: str):
    """Download the generated .bib file (only works after an upload)."""
    raise HTTPException(status_code=400, detail="Use /api/upload endpoint to process and download files")


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
