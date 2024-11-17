import subprocess
import sys
import os
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from pydub import AudioSegment

# Verificar si la librería está instalada y, de no ser así, instalarla.
try:
    import yt_dlp as youtube_dl
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    import yt_dlp as youtube_dl

class VideoDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Descargador de Videos")
        self.root.geometry("400x350")
        self.root.configure(bg="#e6e6e6")

        # Título
        self.title_label = tk.Label(root, text="Descargador de Videos", font=("Helvetica", 16, "bold"), bg="#e6e6e6")
        self.title_label.pack(pady=10)

        # Campo de entrada de URL
        self.url_label = tk.Label(root, text="Ingrese el link del video:", font=("Helvetica", 12), bg="#e6e6e6")
        self.url_label.pack(pady=5)

        self.url_entry = tk.Entry(root, width=40)
        self.url_entry.pack(pady=5)

        # Selección de carpeta de descarga
        self.select_folder_button = tk.Button(root, text="Seleccionar carpeta de destino", command=self.select_folder, bg="#4CAF50", fg="white", font=("Helvetica", 10))
        self.select_folder_button.pack(pady=5)

        self.folder_label = tk.Label(root, text="Carpeta seleccionada: No especificada", font=("Helvetica", 10), bg="#e6e6e6")
        self.folder_label.pack(pady=5)

        # Barra de progreso
        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)

        # Botón de descarga
        self.download_button = tk.Button(root, text="Descargar Video", command=self.descargar_video, bg="#4CAF50", fg="white", font=("Helvetica", 12))
        self.download_button.pack(pady=10)

        # Checkbox para conversión a MP3
        self.convert_to_mp3 = tk.BooleanVar()
        self.convert_checkbox = tk.Checkbutton(root, text="Convertir a MP3", variable=self.convert_to_mp3, bg="#e6e6e6")
        self.convert_checkbox.pack(pady=5)

        # Pie de página
        self.footer_label = tk.Label(root, text="By: Ado", font=("Helvetica", 10, "italic"), bg="#e6e6e6")
        self.footer_label.pack(side="bottom", pady=5)

        # Variable para almacenar la carpeta seleccionada
        self.download_folder = None

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_folder = folder
            self.folder_label.config(text=f"Carpeta seleccionada: {folder}")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percentage = float(d['_percent_str'].strip('%'))
            self.progress['value'] = percentage
            self.root.update_idletasks()
        elif d['status'] == 'finished':
            self.progress['value'] = 100
            self.root.update_idletasks()
            messagebox.showinfo("Descarga completada", f"El archivo se ha guardado en la carpeta:\n{self.download_folder}")

            # Convertir a MP3 si se seleccionó la opción
            if self.convert_to_mp3.get():
                self.convert_to_mp3_file(d['filename'])

    def convert_to_mp3_file(self, video_file):
        try:
            audio = AudioSegment.from_file(video_file)
            mp3_file = os.path.splitext(video_file)[0] + ".mp3"
            audio.export(mp3_file, format="mp3")
            messagebox.showinfo("Conversión completada", f"El archivo se ha convertido a MP3:\n{mp3_file}")
        except Exception as e:
            messagebox.showerror("Error de conversión", f"Hubo un problema al convertir el archivo a MP3:\n{e}")

    def descargar_video(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Por favor ingrese un link de video.")
            return
        if not self.download_folder:
            messagebox.showerror("Error", "Por favor seleccione una carpeta de destino.")
            return

        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],  # Progreso
        }

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                self.progress['value'] = 0  # Reiniciar barra de progreso
                ydl.download([url])
        except Exception as e:
            messagebox.showerror("Error de descarga", f"Hubo un problema al descargar el video:\n{e}")

# Crear la ventana principal
root = tk.Tk()
app = VideoDownloader(root)
root.mainloop()
