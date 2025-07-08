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

## Instalación
No requiere instalación especial. Solo asegúrate de tener Python instalado en tu sistema.

## Uso
Ejecuta el script desde la línea de comandos:

```bash
python bib_checker.py archivo.zip salida.bib
```

- `archivo.zip`: Ruta al archivo `.zip` que contiene los archivos `.tex` y al menos un archivo `.bib`.
- `salida.bib`: Ruta donde se generará el nuevo archivo `.bib` limpio.

### Ejemplo
Supón que tienes un archivo `proyecto.zip` con varios archivos `.tex` y un archivo `referencias.bib`. Para limpiar la bibliografía, ejecuta:

```bash
python bib_checker.py proyecto.zip referencias_limpio.bib
```

Esto generará:
- `referencias_limpio.bib`: Solo con las entradas citadas.
- `remove.bib.bak`: Archivo de respaldo con las entradas eliminadas, en el mismo directorio que el archivo de salida.

## Notas adicionales
- El script solo procesa el primer archivo `.bib` encontrado en el `.zip`.
- Todos los archivos deben estar codificados en UTF-8.
- Si el archivo `.zip` no contiene archivos `.tex` o `.bib`, el script mostrará un error.

## Licencia
Este proyecto se distribuye bajo los términos de la licencia MIT. 