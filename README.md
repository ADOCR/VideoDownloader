## Descripción General

VideoDownloader es una aplicación gráfica que permite a los usuarios descargar videos desde Internet mediante una URL y, opcionalmente, convertir los archivos descargados a formato MP3. La interfaz gráfica está construida con **tkinter**, y las funciones de descarga y conversión utilizan **yt-dlp** y **pydub** respectivamente. El usuario puede seleccionar una carpeta de destino para guardar los archivos.

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
- **ffmpeg** como backend para pydub. Puedes descargarlo desde [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html) y agregarlo al PATH del sistema.

## Funcionalidades

- **Descarga de Videos**: Permite al usuario ingresar una URL y descargar el video en la mejor calidad disponible.
- **Selección de Carpeta de Descarga**: El usuario puede seleccionar la carpeta donde se guardarán los archivos descargados.
- **Conversión a MP3**: Opción para convertir automáticamente el archivo descargado a formato MP3.
- **Barra de Progreso**: Indicador visual del progreso de la descarga.
- **Interfaz Gráfica**: Construida con tkinter para una experiencia amigable y sencilla.

## Instrucciones de Uso

1. **Ejecutar la Aplicación**: Inicia el script de Python para abrir la ventana de la aplicación.
2. **Ingresar URL**: Introduce la URL del video que deseas descargar.
3. **Seleccionar Carpeta de Destino**: Haz clic en "Seleccionar carpeta de destino" para elegir dónde guardar el archivo.
4. **Descargar Video**: Presiona "Descargar Video" para iniciar la descarga.
5. **Conversión a MP3**: Si deseas convertir el archivo descargado a MP3, marca la casilla de verificación "Convertir a MP3".
6. **Ver Progreso**: Observa el progreso de la descarga en la barra de progreso.
7. **Confirmaciones**: Se mostrará un mensaje al finalizar la descarga y la conversión (si corresponde).
