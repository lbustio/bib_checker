"""
Script para limpiar archivos de bibliografía (.bib) eliminando las entradas no citadas en documentos LaTeX (.tex) contenidos en un archivo comprimido (.zip).

Flujo general:
1. El usuario proporciona un archivo .zip que contiene archivos .tex y al menos un archivo .bib.
2. El script extrae todas las claves citadas en los .tex.
3. Lee todas las entradas del .bib y selecciona solo las que han sido citadas.
4. Genera un nuevo archivo .bib limpio y un archivo de respaldo con las entradas eliminadas.
5. Muestra un resumen del proceso por consola.

Ejemplo de uso:
    python bib_checker.py proyecto.zip referencias_limpio.bib

Esto generará:
    - referencias_limpio.bib: solo con las entradas citadas.
    - remove.bib.bak: archivo de respaldo con las entradas eliminadas.
"""

# Importa el módulo para trabajar con archivos comprimidos ZIP
import zipfile
# Importa el módulo de expresiones regulares para buscar patrones en texto
import re
# Importa el módulo para interactuar con el sistema de archivos (rutas, etc.)
import os
# Importa el módulo para manejar argumentos de línea de comandos
import argparse
# Importa una clase para leer archivos binarios como texto (útil al leer archivos dentro del ZIP)
from io import TextIOWrapper
# Importa la librería rich para logs coloridos y atractivos
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import track

console = Console()

def extract_citations(tex_content):
    """
    Extrae todas las claves de citas utilizadas en los archivos .tex.
    Busca comandos \cite, \citep, \citet, etc., y extrae las claves citadas.
    
    Args:
        tex_content (str): Contenido completo de los archivos .tex.
    
    Returns:
        set: Conjunto de claves citadas encontradas en el texto.
    """
    pattern = re.compile(r'\\cite\w*\{([^}]+)\}')  # Busca \cite{...}, \citep{...}, etc.
    citations = set()
    for match in pattern.findall(tex_content):
        # Puede haber varias claves separadas por coma en una sola cita
        for key in match.split(','):
            citations.add(key.strip())
    return citations

def extract_bib_entries(bib_content):
    """
    Extrae todas las entradas de un archivo .bib y las organiza en un diccionario.
    
    Args:
        bib_content (str): Contenido completo del archivo .bib.
    
    Returns:
        dict: Diccionario con claves de entrada como llaves y la entrada completa como valor.
    """
    entries = {}
    current_key = None
    current_entry = []
    inside_entry = False

    for line in bib_content.splitlines():
        if line.strip().startswith('@'):
            # Si ya estábamos procesando una entrada, la guardamos
            if current_key:
                entries[current_key] = '\n'.join(current_entry)
            current_entry = [line]
            inside_entry = True
            # Extraemos la clave de la entrada, por ejemplo: @article{clave,
            key_match = re.match(r'@\w+\{([^,]+),', line)
            current_key = key_match.group(1).strip() if key_match else None
        elif inside_entry:
            current_entry.append(line)

    # Guardamos la última entrada si existe
    if current_key:
        entries[current_key] = '\n'.join(current_entry)

    return entries

def process_zip(zip_path, output_bib_path):
    """
    Procesa un archivo .zip que contiene archivos .tex y un .bib, generando un nuevo .bib limpio.
    Maneja excepciones comunes y muestra mensajes claros al usuario.
    
    Args:
        zip_path (str): Ruta al archivo .zip de entrada.
        output_bib_path (str): Ruta donde se guardará el nuevo archivo .bib limpio.
    """
    try:
        console.rule("[bold blue]Inicio del proceso de limpieza de bibliografía")
        with zipfile.ZipFile(zip_path, 'r') as z:
            # Listamos los archivos .tex y .bib dentro del zip
            tex_files = [f for f in z.namelist() if f.endswith('.tex')]
            bib_files = [f for f in z.namelist() if f.endswith('.bib')]

            console.log(f"[bold cyan]Archivos .tex encontrados:[/] {len(tex_files)}")
            console.log(f"[bold cyan]Archivos .bib encontrados:[/] {len(bib_files)}")

            if not bib_files:
                raise ValueError("No se encontró ningún archivo .bib en el ZIP.")
            if not tex_files:
                raise ValueError("No se encontró ningún archivo .tex en el ZIP.")

            bib_file = bib_files[0]  # Solo se toma el primer .bib encontrado
            all_tex = ''
            # Leemos y concatenamos el contenido de todos los .tex
            for tex_file in track(tex_files, description="[green]Leyendo archivos .tex..."):
                try:
                    with z.open(tex_file) as f:
                        all_tex += TextIOWrapper(f, encoding='utf-8').read()
                except UnicodeDecodeError:
                    console.log(f"[bold red]Error:[/] El archivo {tex_file} no está codificado en UTF-8.")
                    return

            console.log("[bold green]Extrayendo claves citadas de los archivos .tex...")
            cited_keys = extract_citations(all_tex)
            console.log(f"[bold green]Total de claves citadas encontradas:[/] {len(cited_keys)}")

            # Leemos el contenido del .bib
            try:
                with z.open(bib_file) as f:
                    bib_content = TextIOWrapper(f, encoding='utf-8').read()
            except UnicodeDecodeError:
                console.log(f"[bold red]Error:[/] El archivo {bib_file} no está codificado en UTF-8.")
                return

            console.log("[bold green]Extrayendo entradas del archivo .bib...")
            all_entries = extract_bib_entries(bib_content)
            console.log(f"[bold green]Total de entradas en el .bib original:[/] {len(all_entries)}")

            # Filtramos las entradas citadas y las no citadas
            used_entries = {k: v for k, v in all_entries.items() if k in cited_keys}
            removed_entries = {k: v for k, v in all_entries.items() if k not in cited_keys}

            # Guardamos el nuevo .bib solo con las entradas citadas
            try:
                with open(output_bib_path, 'w', encoding='utf-8') as f:
                    f.write('\n\n'.join(used_entries.values()))
                console.log(f"[bold blue]Archivo limpio generado:[/] {output_bib_path}")
            except (IOError, OSError) as e:
                console.log(f"[bold red]Error al escribir el archivo de salida {output_bib_path}:[/] {e}")
                return

            # Guardamos las entradas eliminadas en un archivo de respaldo
            bak_path = os.path.join(os.path.dirname(output_bib_path), 'remove.bib.bak')
            try:
                with open(bak_path, 'w', encoding='utf-8') as f:
                    f.write('\n\n'.join(removed_entries.values()))
                console.log(f"[bold yellow]Entradas removidas guardadas en:[/] {bak_path}")
            except (IOError, OSError) as e:
                console.log(f"[bold red]Error al escribir el archivo de respaldo {bak_path}:[/] {e}")
                return

            # Mostramos un resumen del proceso
            resumen = (
                f"[bold green]Resumen de limpieza:[/]\n"
                f"  [bold]Total de entradas en .bib original:[/] {len(all_entries)}\n"
                f"  [bold]Entradas citadas en los .tex:[/] {len(used_entries)}\n"
                f"  [bold]Entradas eliminadas:[/] {len(removed_entries)}\n"
            )
            console.print(Panel(resumen, title="[bold blue]Proceso completado", expand=False))
            console.rule("[bold blue]Fin del proceso")
    except zipfile.BadZipFile:
        console.log(f"[bold red]Error:[/] El archivo '{zip_path}' no es un archivo ZIP válido o está dañado.")
    except FileNotFoundError:
        console.log(f"[bold red]Error:[/] El archivo '{zip_path}' no existe.")
    except PermissionError:
        console.log(f"[bold red]Error:[/] Permiso denegado al acceder a '{zip_path}' o al escribir archivos de salida.")
    except ValueError as ve:
        console.log(f"[bold red]Error:[/] {ve}")
    except Exception as e:
        console.log(f"[bold red]Ocurrió un error inesperado:[/] {e}")

if __name__ == "__main__":
    # Definimos los argumentos de línea de comandos
    parser = argparse.ArgumentParser(
        description="Limpia un .bib eliminando entradas no citadas en archivos .tex contenidos en un .zip."
    )
    parser.add_argument("zipfile", help="Ruta al archivo .zip que contiene los .tex y el .bib")
    parser.add_argument("outputbib", help="Ruta de salida del nuevo archivo .bib limpio")
    args = parser.parse_args()

    # Ejecutamos el proceso principal
    process_zip(args.zipfile, args.outputbib)