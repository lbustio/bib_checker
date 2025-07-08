# bib_checker

Herramienta para limpiar archivos de bibliografía (.bib) eliminando las entradas no citadas en documentos LaTeX (.tex) contenidos en un archivo comprimido (.zip).

## Descripción

`bib_checker` es un script en Python diseñado para facilitar la gestión de bibliografías en proyectos LaTeX. Permite identificar y eliminar automáticamente las entradas de un archivo `.bib` que no son citadas en los archivos `.tex` de un proyecto, ayudando a mantener la bibliografía concisa y relevante.

## Características principales
- Extrae todas las citas utilizadas en los archivos `.tex` dentro de un archivo `.zip`.
- Genera un nuevo archivo `.bib` que solo contiene las entradas citadas.
- Crea un archivo de respaldo con las entradas eliminadas.
- Proporciona un resumen detallado del proceso.

## Requisitos
- Python 3.6 o superior
- [rich](https://github.com/Textualize/rich) (`pip install rich`)

## Instalación
No requiere instalación especial. Solo asegúrate de tener Python y la librería `rich` instalados en tu sistema.

## Uso
Ejecuta el script desde la línea de comandos:

```bash
python bib_checker.py archivo.zip salida.bib
```

- `archivo.zip`: Ruta al archivo `.zip` que contiene los archivos `.tex` y al menos un archivo `.bib`.
- `salida.bib`: Ruta donde se generará el nuevo archivo `.bib` limpio.

### Ejemplo de ejecución y logs

Al ejecutar el script, verás una salida colorida y profesional como la siguiente:

```console
───────────────────────────── Inicio del proceso de limpieza de bibliografía ─────────────────────────────
[cyan]Archivos .tex encontrados:[/] 3
[cyan]Archivos .bib encontrados:[/] 1
[green]Leyendo archivos .tex... 100%|████████████████████████████████████████| 3/3 [00:00<00:00, 1000.00it/s]
[green]Extrayendo claves citadas de los archivos .tex...[/]
[green]Total de claves citadas encontradas:[/] 12
[green]Extrayendo entradas del archivo .bib...[/]
[green]Total de entradas en el .bib original:[/] 25
[blue]Archivo limpio generado:[/] salida.bib
[yellow]Entradas removidas guardadas en:[/] remove.bib.bak
╭───────────────────────────── Proceso completado ─────────────────────────────╮
│ [green]Resumen de limpieza:[/]                                               │
│   [bold]Total de entradas en .bib original:[/] 25                            │
│   [bold]Entradas citadas en los .tex:[/] 12                                  │
│   [bold]Entradas eliminadas:[/] 13                                           │
╰──────────────────────────────────────────────────────────────────────────────╯
───────────────────────────────────── Fin del proceso ─────────────────────────────────────
```

> **Nota:** Los colores pueden variar según el tema de tu terminal. Los mensajes importantes y los errores se muestran en azul, verde, amarillo o rojo para facilitar la lectura y el seguimiento del proceso.

## Notas adicionales
- El script solo procesa el primer archivo `.bib` encontrado en el `.zip`.
- Todos los archivos deben estar codificados en UTF-8.
- Si el archivo `.zip` no contiene archivos `.tex` o `.bib`, el script mostrará un error.

## Licencia
Este proyecto se distribuye bajo los términos de la licencia MIT. 