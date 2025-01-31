import subprocess
import sys
import os
import threading
import torch
import torchaudio  # <--- Se añadió esta importación
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from pydub import AudioSegment
import yt_dlp as youtube_dl
from demucs import pretrained
from demucs.apply import apply_model
from demucs.audio import AudioFile

def verificar_dependencias():
    """Verifica la presencia de ffmpeg y otras dependencias críticas"""
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        messagebox.showerror("Error crítico", 
                             "FFmpeg no está instalado. Es requerido para el funcionamiento del programa.")
        sys.exit(1)

def verificar_e_instalar_librerias():
    """Verifica e instala automáticamente las librerías requeridas."""
    # Diccionario con librerías requeridas
    librerias_requeridas = {
        "torch": "torch",
        "pydub": "pydub",
        "yt_dlp": "yt-dlp",
        "demucs": "demucs",
        "torchaudio": "torchaudio"
    }
    for import_name, pip_name in librerias_requeridas.items():
        try:
            __import__(import_name)
            print(f"La librería '{import_name}' ya está instalada.")
        except ImportError:
            print(f"\nLa librería '{import_name}' no está instalada. Iniciando instalación...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
                print(f"'{import_name}' se ha instalado correctamente.\n")
            except subprocess.CalledProcessError:
                print(f"Error: no se pudo instalar '{import_name}'. "
                      "Por favor, instálala manualmente.")
                sys.exit(1)

# Llamar a las funciones de verificación
verificar_e_instalar_librerias()
verificar_dependencias()

class VideoDownloader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Descargador de Videos Mejorado")
        self.geometry("500x550")
        self.configure(bg="#f0f0f0")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Variables de estado
        self.download_folder = None
        self.is_processing = False
        self.current_task = None
        
        # Cargar modelo Demucs una vez al iniciar
        self.demucs_model = pretrained.get_model(name="htdemucs")
        if torch.cuda.is_available():
            self.demucs_model.cuda()
        
        self.create_widgets()
    
    def create_widgets(self):
        # Estilos
        style = ttk.Style()
        style.configure("TProgressbar", thickness=20)
        
        # Marco principal
        main_frame = ttk.Frame(self)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Elementos de la UI
        self.title_label = ttk.Label(
            main_frame, 
            text="Descargador y Procesador de Videos", 
            font=("Helvetica", 14, "bold")
        )
        self.title_label.pack(pady=10)
        
        # Entrada de URL
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill="x", pady=5)
        
        ttk.Label(url_frame, text="URL del video:").pack(side="left")
        self.url_entry = ttk.Entry(url_frame, width=40)
        self.url_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        # Selección de carpeta
        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill="x", pady=5)
        
        self.select_folder_btn = ttk.Button(
            folder_frame, 
            text="Seleccionar carpeta", 
            command=self.select_folder
        )
        self.select_folder_btn.pack(side="left")
        
        self.folder_label = ttk.Label(
            folder_frame, 
            text="Carpeta no seleccionada",
            foreground="#666666"
        )
        self.folder_label.pack(side="left", padx=5, expand=True, fill="x")
        
        # Opciones de procesamiento
        options_frame = ttk.LabelFrame(main_frame, text="Opciones de procesamiento")
        options_frame.pack(fill="x", pady=10)
        
        self.convert_to_mp3 = tk.BooleanVar()
        self.convert_check = ttk.Checkbutton(
            options_frame, 
            text="Convertir a MP3", 
            variable=self.convert_to_mp3
        )
        self.convert_check.pack(anchor="w", pady=2)
        
        self.separar_pistas = tk.BooleanVar()
        self.separar_check = ttk.Checkbutton(
            options_frame, 
            text="Separar pistas (Demucs)", 
            variable=self.separar_pistas
        )
        self.separar_check.pack(anchor="w", pady=2)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(
            main_frame, 
            style="TProgressbar",
            maximum=100
        )
        self.progress.pack(fill="x", pady=10)
        self.status_label = ttk.Label(
            main_frame, 
            text="Listo",
            foreground="#444444"
        )
        self.status_label.pack()
        
        # Botones de control
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        self.download_btn = ttk.Button(
            btn_frame, 
            text="Iniciar descarga", 
            command=self.iniciar_descarga
        )
        self.download_btn.pack(side="left", padx=5)
        
        self.cancel_btn = ttk.Button(
            btn_frame, 
            text="Cancelar", 
            command=self.cancelar_proceso,
            state="disabled"
        )
        self.cancel_btn.pack(side="left", padx=5)
        
        # Footer
        ttk.Label(
            main_frame, 
            text="By: Ado - v2.0", 
            font=("Helvetica", 8, "italic"), 
            foreground="#888888"
        ).pack(side="bottom", pady=5)
        
        self.update_ui_state()
    
    def update_ui_state(self):
        state = "normal" if not self.is_processing else "disabled"
        self.url_entry["state"] = state
        self.select_folder_btn["state"] = state
        self.convert_check["state"] = state
        self.separar_check["state"] = state
        self.download_btn["state"] = state
        self.cancel_btn["state"] = "normal" if self.is_processing else "disabled"
    
    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_folder = folder
            self.folder_label.config(text=os.path.basename(folder))
    
    def iniciar_descarga(self):
        if not self.validar_entradas():
            return
        
        self.is_processing = True
        self.update_ui_state()
        url = self.url_entry.get()
        
        # Iniciar proceso en un hilo separado
        self.current_task = threading.Thread(
            target=self.ejecutar_proceso_completo,
            args=(url,),
            daemon=True
        )
        self.current_task.start()
        self.verificar_progreso()
    
    def validar_entradas(self):
        if not self.url_entry.get().startswith(("http://", "https://")):
            messagebox.showerror("Error", "Por favor ingrese una URL válida")
            return False
        if not self.download_folder:
            messagebox.showerror("Error", "Seleccione una carpeta de destino")
            return False
        return True
    
    def ejecutar_proceso_completo(self, url):
        try:
            # Descargar el video
            archivo_descargado = self.descargar_video(url)
            
            # Conversión a MP3
            if self.convert_to_mp3.get():
                archivo_procesado = self.convertir_a_mp3(archivo_descargado)
            else:
                archivo_procesado = archivo_descargado
            
            # Separación de pistas
            if self.separar_pistas.get():
                self.separar_pistas_audio(archivo_procesado)
            
            self.actualizar_estado("Proceso completado con éxito")
        except Exception as e:
            self.mostrar_error(f"Error en el proceso: {str(e)}")
        finally:
            self.is_processing = False
    
    def descargar_video(self, url):
        self.actualizar_estado("Iniciando descarga...")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
            'progress_hooks': [self.actualizar_progreso_descarga],
        }
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            ruta_completa = ydl.prepare_filename(info)
            ydl.download([url])
        
        return ruta_completa
    
    def convertir_a_mp3(self, input_path):
        self.actualizar_estado("Convirtiendo a MP3...")
        output_path = os.path.splitext(input_path)[0] + ".mp3"
        
        try:
            audio = AudioSegment.from_file(input_path)
            audio.export(output_path, format="mp3", bitrate="320k")
            os.remove(input_path)  # Eliminar el archivo original
            return output_path
        except Exception as e:
            raise RuntimeError(f"Error en conversión MP3: {str(e)}")
    
    def separar_pistas_audio(self, audio_file):
        """
        Separa las pistas de un archivo de audio usando el comando `demucs` por línea de comandos.
        Además, muestra en la interfaz si usará la GPU (CUDA) o la CPU.
        """
        try:
            # Verifique que el archivo existe
            if not os.path.exists(audio_file):
                raise FileNotFoundError(f"El archivo '{audio_file}' no existe o no es accesible.")
    
            # Directorio de salida para las pistas separadas
            output_dir = os.path.join(self.download_folder, "separated")
            os.makedirs(output_dir, exist_ok=True)
    
            # Decidir si se usará GPU o CPU y mostrarlo en la interfaz
            if torch.cuda.is_available():
                device_cmd = "cuda"
                self.actualizar_estado("Usando la GPU (CUDA) para la separación de pistas.")
            else:
                device_cmd = "cpu"
                self.actualizar_estado("Usando la CPU para la separación de pistas.")
    
            # Armar el comando para Demucs
            command = [
                "demucs",
                "-d", device_cmd,            # GPU o CPU
                "--out", output_dir,         # Carpeta de salida
                audio_file                   # Archivo a separar
            ]
            
            # Ejecutar Demucs como proceso externo
            subprocess.run(command, check=True, text=True)
    
            # Verificar que se crearon pistas
            if not os.listdir(output_dir):
                raise RuntimeError("Las pistas no se generaron correctamente en la carpeta esperada.")
    
            # Mensaje de confirmación
            messagebox.showinfo("Separación completada", f"Las pistas separadas se han guardado en:\n{output_dir}")
    
        except FileNotFoundError as e:
            messagebox.showerror("Error de separación", f"Archivo no encontrado: {e}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error de separación", f"Error al ejecutar Demucs:\n{e}")
        except RuntimeError as e:
            messagebox.showerror("Error de separación", str(e))
        except Exception as e:
            messagebox.showerror("Error de separación", f"Hubo un problema al separar las pistas:\n{e}")
            
    def actualizar_progreso_descarga(self, d):
        if d['status'] == 'downloading' and d.get('total_bytes'):
            porcentaje = (d['downloaded_bytes'] / d['total_bytes']) * 100
            self.progress["value"] = porcentaje
    
    def verificar_progreso(self):
        if self.is_processing:
            self.after(100, self.verificar_progreso)
    
    def actualizar_estado(self, mensaje):
        self.status_label.config(text=mensaje)
        self.update_idletasks()
    
    def mostrar_error(self, mensaje):
        messagebox.showerror("Error", mensaje)
        self.is_processing = False
        self.update_ui_state()
    
    def cancelar_proceso(self):
        if messagebox.askyesno("Confirmar", "¿Desea cancelar el proceso actual?"):
            self.is_processing = False
            self.actualizar_estado("Proceso cancelado por el usuario")
    
    def on_close(self):
        if self.is_processing and not messagebox.askokcancel(
            "Salir", "Hay un proceso en ejecución. ¿Realmente desea salir?"):
            return
        self.destroy()

if __name__ == "__main__":
    app = VideoDownloader()
    app.mainloop()
