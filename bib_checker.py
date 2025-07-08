import zipfile
import re
import os
import argparse
from io import TextIOWrapper

def extract_citations(tex_content):
    pattern = re.compile(r'\\cite\w*\{([^}]+)\}')
    citations = set()
    for match in pattern.findall(tex_content):
        for key in match.split(','):
            citations.add(key.strip())
    return citations

def extract_bib_entries(bib_content):
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

def process_zip(zip_path, output_bib_path):
    with zipfile.ZipFile(zip_path, 'r') as z:
        tex_files = [f for f in z.namelist() if f.endswith('.tex')]
        bib_files = [f for f in z.namelist() if f.endswith('.bib')]

        if not bib_files:
            raise ValueError("No .bib file found in the ZIP.")
        if not tex_files:
            raise ValueError("No .tex files found in the ZIP.")

        bib_file = bib_files[0]
        all_tex = ''
        for tex_file in tex_files:
            with z.open(tex_file) as f:
                all_tex += TextIOWrapper(f, encoding='utf-8').read()

        cited_keys = extract_citations(all_tex)

        with z.open(bib_file) as f:
            bib_content = TextIOWrapper(f, encoding='utf-8').read()

        all_entries = extract_bib_entries(bib_content)

        used_entries = {k: v for k, v in all_entries.items() if k in cited_keys}
        removed_entries = {k: v for k, v in all_entries.items() if k not in cited_keys}

        # Guardar el nuevo .bib
        with open(output_bib_path, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(used_entries.values()))

        # Guardar el .bak con las entradas eliminadas
        bak_path = os.path.join(os.path.dirname(output_bib_path), 'remove.bib.bak')
        with open(bak_path, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(removed_entries.values()))

        # Resumen
        print("Resumen de limpieza:")
        print(f"  Total de entradas en .bib original: {len(all_entries)}")
        print(f"  Entradas citadas en los .tex: {len(used_entries)}")
        print(f"  Entradas eliminadas: {len(removed_entries)}")
        print(f"  Archivo limpio generado: {output_bib_path}")
        print(f"  Entradas removidas guardadas en: {bak_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Limpia un .bib eliminando entradas no citadas en archivos .tex contenidos en un .zip.")
    parser.add_argument("zipfile", help="Ruta al archivo .zip que contiene los .tex y el .bib")
    parser.add_argument("outputbib", help="Ruta de salida del nuevo archivo .bib limpio")
    args = parser.parse_args()

    process_zip(args.zipfile, args.outputbib)