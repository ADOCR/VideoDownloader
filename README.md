## Descripción General

VideoDownloader es una aplicación gráfica que permite a los usuarios descargar videos desde Internet mediante una URL y, opcionalmente, convertir los archivos descargados a formato MP3. Además, incluye la opción de separar las pistas de audio (voces e instrumentos) usando Demucs, aprovechando la GPU si está disponible. La interfaz gráfica está construida con **tkinter**, y las funciones de descarga, conversión y separación utilizan **yt-dlp**, **pydub** y **Demucs** respectivamente. El usuario puede seleccionar una carpeta de destino para guardar los archivos.

## Requisitos Previos

Antes de ejecutar la aplicación, asegúrate de tener instaladas las siguientes dependencias:

- **Python 3.x** (recomendado)
- **yt-dlp** para la descarga de videos:
  ```bash
  pip install yt-dlp
  ```
- **pydub** para la conversión de audio:
  ```bash
  pip install pydub
  ```
- **torch** para el procesamiento con Demucs:
  ```bash
  pip install torch
  ```
- **Demucs** para la separación de pistas:
  ```bash
  pip install demucs
  ```
- **ffmpeg** como backend para pydub y Demucs. Puedes descargarlo desde [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html) y agregarlo al PATH del sistema.

## Funcionalidades

- **Descarga de Videos**: Permite al usuario ingresar una URL y descargar el video en la mejor calidad disponible.
- **Selección de Carpeta de Descarga**: El usuario puede seleccionar la carpeta donde se guardarán los archivos descargados.
- **Conversión a MP3**: Opción para convertir automáticamente el archivo descargado a formato MP3.
- **Separación de Pistas de Audio**: Usando Demucs, se separan las pistas de audio (voces, batería, bajo, etc.) del archivo descargado.
  - **Aprovechamiento de GPU**: Si una GPU compatible está disponible, Demucs la utilizará automáticamente para acelerar el procesamiento.
- **Barra de Progreso**: Indicador visual del progreso de la descarga.
- **Interfaz Gráfica**: Construida con tkinter para una experiencia amigable y sencilla.

## Instrucciones de Uso

1. **Ejecutar la Aplicación**: Inicia el script de Python para abrir la ventana de la aplicación.
2. **Ingresar URL**: Introduce la URL del video que deseas descargar.
3. **Seleccionar Carpeta de Destino**: Haz clic en "Seleccionar carpeta de destino" para elegir dónde guardar el archivo.
4. **Descargar Video**: Presiona "Descargar Video" para iniciar la descarga.
5. **Conversión a MP3**: Si deseas convertir el archivo descargado a MP3, marca la casilla de verificación "Convertir a MP3".
6. **Separación de Pistas**: Si deseas separar las pistas de audio del archivo descargado, marca la casilla de verificación "Separar pistas (usando Demucs)".
7. **Ver Progreso**: Observa el progreso de la descarga en la barra de progreso.
8. **Resultados**:
   - Los archivos descargados estarán en la carpeta seleccionada.
   - Si seleccionaste "Convertir a MP3", los archivos MP3 estarán en la misma carpeta.
   - Si seleccionaste "Separar pistas", las pistas estarán en una subcarpeta llamada `separated`.
