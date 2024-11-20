import subprocess
import sys
import os
import torch
import tkinter as tk
from tkinter import messagebox, ttk, filedialog

# Verificar e instalar librerías necesarias
def verificar_librerias(librerias):
    faltantes = []
    for libreria in librerias:
        try:
            __import__(libreria)
        except ImportError:
            faltantes.append(libreria)

    if faltantes:
        print(f"Instalando librerías faltantes: {faltantes}")
        for libreria in faltantes:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", libreria])
                print(f"Librería {libreria} instalada correctamente.")
            except subprocess.CalledProcessError as e:
                print(f"Error al instalar {libreria}: {e}")
                messagebox.showerror("Error", f"Error al instalar la librería: {libreria}")
                return False
    return True


# Dependencias requeridas
librerias_requeridas = ["yt_dlp", "pydub", "torch", "demucs"]

if not verificar_librerias(librerias_requeridas):
    sys.exit("No se pudieron instalar las dependencias necesarias.")

# Importar librerías después de la verificación
from pydub import AudioSegment
import yt_dlp as youtube_dl
from demucs import pretrained
from demucs.apply import apply_model


class VideoDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Descargador de Videos")
        self.root.geometry("400x400")
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

        # Checkbox para separar pistas
        self.separar_pistas = tk.BooleanVar()
        self.separar_checkbox = tk.Checkbutton(root, text="Separar pistas (usando Demucs)", variable=self.separar_pistas, bg="#e6e6e6")
        self.separar_checkbox.pack(pady=5)

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

            # Separar pistas si se seleccionó la opción
            if self.separar_pistas.get():
                self.separar_pistas_audio(d['filename'])

    def convert_to_mp3_file(self, video_file):
        try:
            audio = AudioSegment.from_file(video_file)
            mp3_file = os.path.splitext(video_file)[0] + ".mp3"
            audio.export(mp3_file, format="mp3")
            messagebox.showinfo("Conversión completada", f"El archivo se ha convertido a MP3:\n{mp3_file}")
        except Exception as e:
            messagebox.showerror("Error de conversión", f"Hubo un problema al convertir el archivo a MP3:\n{e}")

    def separar_pistas_audio(self, audio_file):
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = pretrained.get_model('htdemucs').to(device)
            output_dir = os.path.join(self.download_folder, "separated")
            os.makedirs(output_dir, exist_ok=True)

            print(f"Separando pistas de: {audio_file}")
            apply_model(model, audio_file, output_dir, device=device)
            messagebox.showinfo("Separación completada", f"Las pistas separadas se han guardado en:\n{output_dir}")
        except Exception as e:
            messagebox.showerror("Error de separación", f"Hubo un problema al separar las pistas:\n{e}")

    def descargar_video(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Por favor ingrese un link de video.")
            return
        if not self.download_folder:
            messagebox.showerror("Error", "Por favor seleccione una carpeta de destino.")
            return

        ydl_opts = {
            'format': 'bestaudio/best',
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
root = tk.Tk()
app = VideoDownloader(root)
root.mainloop()
