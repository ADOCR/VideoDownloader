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
# Cambios entre la versión anterior y la nueva

A continuación se detallan los **principales cambios** introducidos en la versión nueva comparada con la versión anterior:

## 1. Verificación y gestión de dependencias
- **Versión Anterior**:
  - Verificaba e instalaba las dependencias llamando directamente a `verificar_e_instalar_librerias(librerias_requeridas)`, recibiendo una lista como parámetro.
  - Se centraba en las librerías: `yt_dlp`, `pydub`, `torch`, `demucs`.

- **Versión Nueva**:
  - Ahora se tiene un **diccionario** para las dependencias, incluyendo también `torchaudio`.
  - Se llama a `verificar_e_instalar_librerias()` y luego a `verificar_dependencias()` para comprobar que `ffmpeg` esté instalado.
  - Cada librería se importa dinámicamente y se instala si no está presente.
  - Revisa explícitamente que `ffmpeg` exista en el sistema.

## 2. Clase principal de la aplicación
- **Versión Anterior**:
  - La clase `VideoDownloader` era un *componente* de Tkinter, pero no heredaba de `tk.Tk`; en su constructor recibía un `root` de Tk.
  - Interfaz más sencilla, con menos opciones y sin manejo de hilos para el proceso de descarga.

- **Versión Nueva**:
  - Ahora la clase `VideoDownloader` **hereda** directamente de `tk.Tk`, por lo que se instancia como `app = VideoDownloader()`.
  - Se define en el método `__init__()` la creación de widgets, se ajusta el tamaño a `500x550` y se cambia el fondo.
  - Se utiliza `protocol("WM_DELETE_WINDOW", self.on_close)` para controlar el cierre de la ventana.
  - Se crea un marco principal (`main_frame`) y se ubican dentro todos los elementos de la interfaz.
  - Se incluyen métodos de control de estado (`update_ui_state`) y la posibilidad de *cancelar* un proceso en marcha.

## 3. Nuevo enfoque para la descarga y procesamiento
- **Versión Anterior**:
  - Se utilizaba un `progress_hook` para la descarga (mostrando el progreso con la barra `ttk.Progressbar`).
  - Una vez descargado, se llamaba a la conversión a MP3 (opcional) y luego, si se elegía, a `separar_pistas_audio()` invocando a **Demucs por línea de comandos**.

- **Versión Nueva**:
  - Separó el proceso completo en el método `iniciar_descarga()`, que lanza un hilo (`threading.Thread`) para no bloquear la interfaz.
  - El método `ejecutar_proceso_completo(url)` maneja descarga, conversión y separación de pistas secuencialmente.
  - El progreso de descarga se actualiza con `actualizar_progreso_descarga`, usando la opción `progress_hooks` de `yt_dlp`.

## 4. Integración con Demucs
- **Versión Anterior**:
  - **Siempre** invocaba Demucs a través de `subprocess.run(["demucs", ...])`.
  - Guardaba los archivos separados en una carpeta `separated`.

- **Versión Nueva** (tal como se mostró originalmente):
  - Incluye lógica para usar Demucs **como librería**, llamando a `apply_model`, cargando el modelo con `pretrained.get_model`.
  - Sin embargo, **en el ejemplo final** se regresó a `subprocess.run` para la separación de pistas (pero dentro del marco de la clase nueva).
  - **Mensaje de GPU**: ahora, antes de invocar Demucs por CLI, muestra si va a usar `cuda` o `cpu`.

## 5. Manejo de eventos y cancelación
- **Versión Anterior**:
  - No ofrecía botón para cancelar el proceso.
  - La interfaz quedaba bloqueada durante la descarga o el procesamiento.

- **Versión Nueva**:
  - Agrega un botón “Cancelar” que llama a `cancelar_proceso()`.
  - Usa la variable `self.is_processing` para desactivar o reactivar widgets en la interfaz (`update_ui_state`).
  - Implementa `verificar_progreso()` para reactivar la interfaz una vez termina el hilo.

## 6. Mejoras en la interfaz (Tkinter)
- **Versión Anterior**:
  - Ventana de tamaño `400x450`.
  - Menos opciones de personalización en la interfaz (colores, textos).
  - Elementos dispuestos directamente en `root`.

- **Versión Nueva**:
  - Ventana de tamaño `500x550`, estilos y fuentes diferentes.
  - Uso de `ttk.LabelFrame`, `ttk.Progressbar` con estilo, una etiqueta de estado (`self.status_label`).
  - Mensajes de estado con `self.actualizar_estado(mensaje)`.
  - Se muestra un pie de página (`By: Ado - v2.0`).

## 7. Integración de `torchaudio`
- **Versión Anterior**:
  - Usaba `pydub` para la conversión a MP3, pero no usaba `torchaudio`.
  - Invocaba Demucs por CLI, sin necesidad de manipular tensores manualmente.

- **Versión Nueva**:
  - **Importa** `torchaudio` para la posibilidad de separar pistas en memoria (aunque finalmente se regresó a `subprocess.run`). 
  - Verifica e instala automáticamente `torchaudio` si está ausente.

---

**En conclusión**, la versión nueva introduce:
- **Verificaciones más robustas** de dependencias (incluyendo `torchaudio` y `ffmpeg`).  
- **Clase Tkinter heredada de `tk.Tk`** en lugar de recibir un `root`.  
- **Uso de hilos** para no bloquear la interfaz durante la descarga/conversión.  
- **Opción de usar Demucs por CLI** con un mensaje específico de GPU/CPU.  
- Una **interfaz más completa y dinámica**, con notificaciones de estado y un flujo centralizado de descarga + procesamiento.

# Comparativo de Versiones - VideoDownloader

## Versión Anterior vs Versión Mejorada (v2.0)

### 1. Gestión de Dependencias
| **Característica**             | **Versión Anterior**                          | **Versión Mejorada**                          |
|---------------------------------|-----------------------------------------------|------------------------------------------------|
| Verificación de FFmpeg         | No existía                                    | Se añadió verificación inicial                |
| Instalación automática         | Solo librerías básicas                       | Lista extendida con torchaudio                |
| Manejo de errores              | Básico                                        | Mensajes detallados por librería              |

### 2. Interfaz de Usuario
| **Característica**             | **Versión Anterior**                          | **Versión Mejorada**                          |
|---------------------------------|-----------------------------------------------|------------------------------------------------|
| Diseño                          | Widgets básicos de tkinter                   | Uso de ttk para mejor apariencia              |
| Estado de la UI                | Sin gestión de estados                       | Bloqueo de controles durante procesos         |
| Feedback visual                | Barra de progreso simple                     | Etiqueta de estado + barra de progreso mejorada|
| Botón de cancelación           | No existía                                    | Se añadió con confirmación                    |

### 3. Funcionalidades Principales
| **Característica**             | **Versión Anterior**                          | **Versión Mejorada**                          |
|---------------------------------|-----------------------------------------------|------------------------------------------------|
| Separación de pistas           | Usaba API directa de Demucs                  | Implementación con subproceso externo         |
| Conversión a MP3               | Calidad por defecto                          | Bitrate alto (320kbps)                        |
| Manejo de GPU                  | No mostraba información                      | Detección y notificación de uso de CUDA       |
| Procesamiento en paralelo      | Secuencial                                   | Usa threading para no bloquear la UI          |

### 4. Manejo de Errores
| **Característica**             | **Versión Anterior**                          | **Versión Mejorada**                          |
|---------------------------------|-----------------------------------------------|------------------------------------------------|
| Validación de URL              | Solo verificación de no vacío                | Chequea formato http/https                    |
| Manejo de excepciones          | Genérico                                     | Específico por tipo de error                  |
| Mensajes de error              | Básicos                                      | Detallados con información técnica            |

### 5. Mejoras de Código
```python
# Cambio significativo en separación de pistas
# Versión anterior (API directa):
wav = AudioFile(audio_path).read(stream=0)

# Versión nueva (subproceso externo):
command = [
    "demucs",
    "-d", device_cmd,
    "--out", output_dir,
    audio_file
]
subprocess.run(command, check=True, text=True)
