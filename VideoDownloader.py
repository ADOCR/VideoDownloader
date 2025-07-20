import importlib
import subprocess
import sys
import threading
import time
import logging
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pydub import AudioSegment
import yt_dlp as youtube_dl
import torch
import re

# ------------------- VERIFICACIÓN DE MÓDULOS -------------------
required = {
    "torch": "torch",
    "torchaudio": "torchaudio",
    "pydub": "pydub",
    "yt_dlp": "yt-dlp",
    "demucs": "demucs",
}

def _check_pkg(name):
    try:
        importlib.import_module(name)
        return True
    except ImportError:
        return False

def _install_pkg(pip_name):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])

def ensure_requirements():
    for mod, pip_name in required.items():
        if not _check_pkg(mod):
            print(f"Instalando {mod}…")
            _install_pkg(pip_name)

# -------------- VERIFICACIÓN DE FFMPEG ------------------------
def ensure_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        messagebox.showerror("Error", "FFmpeg no está instalado o no se encuentra en PATH")
        sys.exit(1)

# ------------------------ LOGGING -----------------------------
logging.basicConfig(filename="app.log", level=logging.INFO,
                    format="%(asctime)s %(levelname)s: %(message)s")

# ------------------- UTILIDAD: NOMBRE SEGURO -----------------
def safe_filename(name):
    name = name.strip()
    name = re.sub(r"[^A-Za-z0-9 ._-]+", "_", name)
    name = re.sub(r"^[ ._-]+", "", name)
    name = re.sub(r"_+", "_", name)
    return name or "audio"

# --------------------- CLASE PRINCIPAL ------------------------
class VideoDownloader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Descargador de Videos Mejorado")
        self.geometry("560x625")
        self.configure(bg="#f7f7f7")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Estado
        self.download_folder = None
        self.is_processing = False
        self.cancel_event = threading.Event()
        self.demucs_model = None

        self.build_ui()

    def build_ui(self):
        ttk.Style().configure("TProgressbar", thickness=18)
        frame = ttk.Frame(self); frame.pack(padx=20, pady=20, fill="both", expand=True)

        ttk.Label(frame, text="Descargador y Procesador de Videos", font=("Helvetica", 15, "bold")).pack(pady=10)

        # URL
        fr_url = ttk.Frame(frame); fr_url.pack(fill="x", pady=6)
        ttk.Label(fr_url, text="URL:").pack(side="left")
        self.ent_url = ttk.Entry(fr_url); self.ent_url.pack(side="left", fill="x", expand=True, padx=5)

        # Carpeta
        fr_fold = ttk.Frame(frame); fr_fold.pack(fill="x", pady=6)
        ttk.Button(fr_fold, text="Carpeta destino", command=self.choose_folder).pack(side="left")
        self.lbl_fold = ttk.Label(fr_fold, text="No seleccionada", foreground="#666"); self.lbl_fold.pack(side="left", padx=6)

        # Opciones
        lf = ttk.LabelFrame(frame, text="Opciones"); lf.pack(fill="x", pady=10)
        self.var_mp3 = tk.BooleanVar()
        ttk.Checkbutton(lf, text="Convertir a MP3", variable=self.var_mp3).pack(anchor="w")
        self.var_sep = tk.BooleanVar()
        ttk.Checkbutton(lf, text="Separar pistas (Demucs)", variable=self.var_sep).pack(anchor="w")
        self.keep_original = tk.BooleanVar(value=True)
        ttk.Checkbutton(lf, text="Conservar archivo original", variable=self.keep_original).pack(anchor="w")

        # Estado
        self.lbl_status = ttk.Label(frame, text="Listo"); self.lbl_status.pack(pady=5)
        self.pb = ttk.Progressbar(frame, maximum=100); self.pb.pack(fill="x", pady=5)

        # Botones
        fr_btn = ttk.Frame(frame); fr_btn.pack(pady=10)
        self.bt_start = ttk.Button(fr_btn, text="Iniciar", command=self.start); self.bt_start.pack(side="left", padx=5)
        self.bt_cancel = ttk.Button(fr_btn, text="Cancelar", state="disabled", command=self.cancel); self.bt_cancel.pack(side="left", padx=5)

        ttk.Label(frame, text="By Ado", font=("Helvetica", 8, "italic"), foreground="#888").pack(side="bottom")
        self.update_ui()

    def update_ui(self):
        st = "disabled" if self.is_processing else "normal"
        self.ent_url["state"] = st; self.bt_start["state"] = st
        self.bt_cancel["state"] = "normal" if self.is_processing else "disabled"

    def choose_folder(self):
        d = filedialog.askdirectory()
        if d:
            self.download_folder = Path(d)
            self.lbl_fold.config(text=self.download_folder.name)

    def start(self):
        url = self.ent_url.get().strip()
        if not url.startswith(("http://", "https://")):
            messagebox.showerror("Error", "URL inválida"); return
        if not self.download_folder:
            messagebox.showerror("Error", "Seleccione carpeta destino"); return
        self.is_processing = True; self.cancel_event.clear(); self.set_status("Preparando…", 0); self.update_ui()
        threading.Thread(target=self.workflow, args=(url,), daemon=True).start()

    def cancel(self):
        if self.is_processing and messagebox.askyesno("Cancelar", "¿Detener proceso en curso?"):
            self.cancel_event.set()
            self.set_status("Cancelando…", 0)

    def on_close(self):
        if self.is_processing and not messagebox.askokcancel("Salir", "Hay un proceso en curso ¿salir?"):
            return
        self.cancel_event.set(); self.destroy()

    def set_status(self, text, progress=None):
        def _set():
            self.lbl_status.config(text=text)
            if progress is not None:
                self.pb["value"] = progress
        self.after(0, _set)

    def show_error(self, message):
        self.after(0, lambda: messagebox.showerror("Error", message))

    def workflow(self, url):
        try:
            path = self.descargar(url)
            if self.cancel_event.is_set(): raise Exception("cancelled")
            if self.var_mp3.get():
                path = self.convert_mp3(path)
            if self.cancel_event.is_set(): raise Exception("cancelled")
            if self.var_sep.get():
                self.separar_pistas(path)
            self.set_status("Completado", 100)
        except Exception as e:
            if str(e) == "cancelled":
                self.set_status("Proceso cancelado", 0)
            else:
                logging.error(f"Error: {e}", exc_info=True)
                self.set_status("Error", 0)
                self.show_error(str(e))
        finally:
            self.is_processing = False
            self.update_ui()

    def descargar(self, url):
        self.set_status("Descargando…", 0)
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(self.download_folder / '%(title)s.%(ext)s'),
            'quiet': True,
            'progress_hooks': [self.hook_progress],
            'noplaylist': True,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            safe_title = safe_filename(info.get('title', 'video'))
            print(f"Título seguro: {safe_title}")  # Debug
            ext = info['ext']
            out_path = self.download_folder / f"{safe_title}.{ext}"
            info['title'] = safe_title  # For outtmpl
            ydl.download([url])
        print(f"Archivo descargado en: {out_path}")  # Debug
        return out_path

    def hook_progress(self, d):
        if self.cancel_event.is_set():
            raise youtube_dl.utils.DownloadError("cancelled")
        if d.get('status') == 'downloading' and d.get('total_bytes'):
            pct = d['downloaded_bytes'] * 100 / d['total_bytes']
            self.set_status(f"Descargando… {pct:0.1f}%", pct)

    def convert_mp3(self, src):
        self.set_status("Convirtiendo a MP3…", 0)
        print(f"Intentando convertir archivo: {src}")  # Debug
        if not src.exists():
            raise Exception(f"El archivo no fue encontrado: {src}")
        dst = src.with_suffix(".mp3")
        try:
            AudioSegment.from_file(src).export(dst, format="mp3", bitrate="320k")
            # Solo borra el original si el usuario lo decidió
            if not self.keep_original.get():
                src.unlink()
        except Exception as e:
            raise Exception("Error al convertir a MP3: " + str(e))
        print(f"Archivo MP3 generado: {dst}")  # Debug
        return dst

    def separar_pistas(self, src):
        self.set_status("Separando pistas…", 0)
        outdir = self.download_folder / "separated"
        outdir.mkdir(exist_ok=True)
        if self.demucs_model is None:
            from demucs import pretrained
            self.demucs_model = pretrained.get_model(name="htdemucs")
            if torch.cuda.is_available():
                self.demucs_model.cuda()
        cmd = [
            "demucs",
            "-d", "cuda" if torch.cuda.is_available() else "cpu",
            "--out", str(outdir),
            str(src)
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        while proc.poll() is None:
            if self.cancel_event.is_set():
                proc.terminate(); raise Exception("cancelled")
            time.sleep(0.5)
        if proc.returncode != 0:
            raise Exception("Error en Demucs (separación de pistas)")

# --------------------------- MAIN ----------------------------
if __name__ == "__main__":
    ensure_requirements()
    ensure_ffmpeg()
    app = VideoDownloader()
    app.mainloop()
