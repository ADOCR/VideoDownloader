## Descripción General

**VideoDownloader v2.2** es una aplicación gráfica en Python para descargar audio de cualquier URL compatible con *yt-dlp*, convertirlo a **MP3 320 kbps** y separar sus pistas con **Demucs** (usando GPU si hay CUDA disponible). Incluye control de errores avanzado, manejo de nombres de archivo seguros, barra de progreso, botón Cancelar y chequeo automático de dependencias.

- Interfaz nativa y ligera (Tkinter + ttk).
- Descarga robusta mediante **yt-dlp**, compatible con streams HLS/fragmentados.
- Proceso en **segundo plano** con threading: la UI nunca se congela.
- **Botón Cancelar** que detiene cualquier paso (descarga, conversión, separación) de inmediato y seguro.
- **Chequeo de FFmpeg** y dependencias al iniciar, instalación automática si falta algo.
- **Logs de errores** en `app.log` para fácil depuración.
- Nombres de archivo a prueba de errores de Windows/Linux.

---

## Requisitos Previos

| Paquete                      | Uso                     | Instalación                                                                                      |
| ---------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------ |
| Python ≥ 3.9                 | Lenguaje                | Instalador oficial o Conda                                                                       |
| ffmpeg                       | Backend de audio/HLS    | Descarga: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html) → Añadir a `PATH` |
| yt‑dlp 2025.06.09 o superior | Descarga de vídeo/audio | `pip install -U yt-dlp`                                                                          |
| pydub                        | Conversión a MP3        | `pip install pydub`                                                                              |
| torch ≥ 2.2                  | Backend Demucs          | `pip install torch --index-url https://download.pytorch.org/whl/cu118` (o `cpu`)                 |
| torchaudio                   | Requerido por Demucs    | `pip install torchaudio --index-url https://download.pytorch.org/whl/cu118`                      |
| demucs v4                    | Separar pistas          | `pip install demucs`                                                                             |

> **Tip Conda**  
> Si usas Conda, basta:  
> `conda install -c conda-forge yt-dlp pydub demucs ffmpeg`  
> `conda install pytorch torchaudio pytorch-cuda=12 -c pytorch -c nvidia`

---

## Funcionalidades

- **Descargar audio** en la mejor calidad (`bestaudio/best`).
- **Conversión a MP3** (320 kbps) tras la descarga (opcional).
- **Separación de pistas** (`vocals`, `drums`, `bass`, `other`) usando Demucs v4 (opcional).
- **Uso automático de GPU** si hay CUDA; si no, usa CPU.
- **Barra de progreso** (0-100 %) y estado textual en la interfaz.
- **Botón CANCELAR** para abortar cualquier proceso de forma segura.
- **Chequeo e instalación automática de dependencias** en el primer arranque.
- **Nombres de archivo seguros** para evitar errores en sistemas de archivos.
- **Log de errores** en `app.log` para depuración.
- **Manejo robusto de errores**: se informa cualquier fallo con mensajes claros y detalles en el log.

---

## Funcionalidades

- **Descargar audio** en la mejor calidad disponible (`bestaudio/best`).
- **Conversión a MP3** (320 kbps) tras la descarga.
- **Separación de pistas** (`vocals`, `drums`, `bass`, `other`) usando Demucs v4.
- **Uso automático de GPU** si hay CUDA; si no, corre en CPU.
- **Barra de progreso + etiqueta dinámica** (xx %).
- **Botón CANCELAR** detiene de forma segura y reactiva la interfaz.
- **Detección y (auto)instalación de dependencias** en el primer arranque.
- **Chequeo de FFmpeg** al iniciar; avisa si no está en el PATH.

---

## Instrucciones de Uso

1. **Clona o descarga** este repo.
2. Entra al directorio y ejecuta:
   ```bash
   python video_downloader.py
   ```
3. **URL** – pega el enlace del vídeo / pista.
4. **Carpeta destino** – elige dónde guardar.
5. (Opcional) **Convertir a MP3**.
6. (Opcional) **Separar pistas (Demucs)**.
7. Haz click en **Iniciar**.
8. Observa el progreso. Puedes **Cancelar** en cualquier momento.
9. Resultados:
   - Archivo `*.m4a` (o `*.mp3`) en la carpeta seleccionada.
   - Pistas separadas en `separated/<titulo>/` si habilitaste Demucs.

---

## Historial de Cambios
### v2.2 (2025‑07‑20)
- **Nueva Licencia:** Se adopta la **HIPPOCRATIC-CR-ADOCR License v1.0** (20 de junio de 2025), que restringe el uso del software únicamente a fines éticos, educativos y culturales de acuerdo a la legislación costarricense y estándares internacionales de derechos humanos.  
- El archivo LICENSE contiene el texto completo de la nueva licencia.
- **Robustez en nombres de archivo:** elimina caracteres problemáticos y previene errores por rutas inválidas.
- **Verificación de existencia** antes de conversión a MP3 para evitar errores si el archivo no está presente.
- **Mensajes de depuración (debug prints)** muestran la ruta real de descarga y conversión.
- **Sincronización de cierre con hilos activos:** el cierre de la ventana ahora espera a que terminen los hilos, evitando errores de Tkinter.
- **Log de errores** en `app.log` para facilitar la depuración.
- **Manejo de errores mejorado:** se muestran mensajes claros en la interfaz y detalles en el log.
- **Actualizaciones en la interfaz:** todo cambio de la UI se hace mediante el hilo principal (`after`), evitando conflictos de hilos.

### v2.1 (2025‑06‑20)

- **Descarga FFmpeg‑HLS forzada** (`hls_prefer_ffmpeg=True`) → corrige error *fragment not found* cuando YouTube usa SSAP.
- **Retry de fragmentos** y *skip* de fragmentos con 404.
- **UI:** progreso determinístico (0‑100 %) y estado textual.
- **Proceso Demucs:** polling no‑bloqueante + terminación segura en Cancelar.
- **Refactor:** clase principal hereda `tk.Tk`; métodos `start()`, `cancel()`, `workflow()`.

### v2.0 (2025‑06‑15)

- Migración completa a *threading*, barra de progreso y botón Cancelar.
- Instalación dinámica de dependencias & verificación de FFmpeg.
- Soporte de GPU (CUDA) para Demucs; mensaje de modo usado.
- Conversión a MP3 con pydub a 320 kbps.
- Interfaz rediseñada con `ttk.Style()`.

### v1.x (2024)

- Descarga básica con yt‑dlp.
- Conversión opcional a MP3.
- Separación de pistas invocando Demucs por CLI.

---

## Licencia

MIT © Adonis 2025


