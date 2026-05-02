# bib_checker

Tool to clean bibliography files (.bib) by removing entries not cited in LaTeX documents (.tex) contained in a ZIP archive.

## Description

`bib_checker` is a Python script designed to simplify bibliography management in LaTeX projects. It identifies and automatically removes entries from a `.bib` file that are not cited in the project's `.tex` files, keeping the bibliography concise and relevant.

## Features

- Extracts all citations from `.tex` files inside a `.zip`.
- Generates a new `.bib` file containing only cited entries.
- Creates a backup file with removed entries.
- Web interface with drag-and-drop upload, statistics, and entry review.

## Requirements

- Python 3.11+
- conda (recommended) or pip

## Installation

### Using conda (recommended)

```bash
conda env create -f environment.yaml
conda activate bib_checker
```

### Using pip

```bash
pip install -r requirements.txt
```

## Usage

### Web Interface

```bash
python app.py
```

Open `http://localhost:8000` in your browser. Drag and drop your ZIP file, view detailed statistics, review cited and removed entries, and download the cleaned `.bib`.

### Command Line

```bash
python bib_checker.py archivo.zip salida.bib
```

- `archivo.zip`: Path to the `.zip` file containing `.tex` and at least one `.bib` file.
- `salida.bib`: Path where the cleaned `.bib` will be generated.

### Example Output

```
===============================================================================
 Bib bibliography cleaning process started
===============================================================================
Archivos .tex encontrados: 3
Archivos .bib encontrados: 1
Reading .tex files... 100% |################| 3/3
Extracting cited keys from .tex files...
Total cited keys found: 12
Extracting entries from .bib file...
Total entries in original .bib: 25
Clean file generated: salida.bib
Removed entries saved to: remove.bib.bak
===============================================================================
 Cleaning summary:
   Total entries in original .bib: 25
   Entries cited in .tex: 12
   Entries removed: 13
===============================================================================
 Process completed
```

## Notes

- Only the first `.bib` file found in the `.zip` is processed.
- All files must be UTF-8 encoded.
- The `.zip` must contain at least one `.tex` and one `.bib` file.

## License

This project is distributed under the terms of the MIT License.
