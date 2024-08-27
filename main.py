import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pyaudio
import threading
from datetime import datetime
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import soundfile as sf

class SoundMasterPro:
    def __init__(self, master):
        self.master = master
        self.master.title('SoundMaster Pro')
        self.master.geometry('900x560')
        self.master.configure(bg='#2c3e50')

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()

        self.recording_event = threading.Event()
        self.audio_thread = None
        self.timestamp = 0
        self.audio_data = []
        self.save_directory = os.path.expanduser("~")
        self.running = True
        self.plot_after_id = None
        self.clock_after_id = None

        self.create_widgets()

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def configure_styles(self):
        self.style.configure('TButton', font=('Roboto', 12), padding=10, relief='flat', background='#3498db', foreground='white')
        self.style.map('TButton', background=[('pressed', '#2980b9'), ('active', '#2980b9')])
        self.style.configure('TLabel', font=('Roboto', 12), background='#2c3e50', foreground='white')
        self.style.configure('TFrame', background='#34495e')
        self.style.configure('TNotebook', background='#2c3e50', foreground='white')
        self.style.configure('TNotebook.Tab', padding=[20, 10], font=('Roboto', 12))

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(pady=20, fill='both', expand=True)

        self.recording_frame = ttk.Frame(self.notebook, padding=20)
        self.library_frame = ttk.Frame(self.notebook, padding=20)
        self.settings_frame = ttk.Frame(self.notebook, padding=20)
        self.about_frame = ttk.Frame(self.notebook, padding=20)

        self.notebook.add(self.recording_frame, text='Gravação')
        self.notebook.add(self.library_frame, text='Biblioteca')
        self.notebook.add(self.settings_frame, text='Configurações')
        self.notebook.add(self.about_frame, text='Sobre')

        self.create_recording_widgets()
        self.create_library_widgets()
        self.create_settings_widgets()
        self.create_about_widgets()

    def create_recording_widgets(self):
        self.app_title = ttk.Label(self.recording_frame, text="SoundMaster Pro", font=("Roboto", 24, 'bold'))
        self.app_title.grid(row=0, column=0, columnspan=4, pady=10)

        self.clock_label = ttk.Label(self.recording_frame, text="", font=("Roboto", 42, 'bold'))
        self.clock_label.grid(row=0, column=5, columnspan=4, pady=5)

        self.instructions = ttk.Label(self.recording_frame, text="Pressione 'Gravar' para iniciar a gravação\nPressione 'Parar' para salvar e encerrar a gravação", justify='center')
        self.instructions.grid(row=1, column=0, columnspan=4, pady=10)

        self.timestamp_label = ttk.Label(self.recording_frame, text="Duração: 0.00 s")
        self.timestamp_label.grid(row=1, column=5, columnspan=4, pady=10)

        self.activity_indicator = tk.Label(self.recording_frame, text="Inativo", bg='#e74c3c', fg='white', font=("Roboto", 16), width=20, height=2)
        self.activity_indicator.grid(row=3, column=0, columnspan=4, pady=20)

        self.button_frame = tk.Frame(self.recording_frame, bg='#34495e')
        self.button_frame.grid(row=3, column=5, columnspan=4, pady=10)

        self.start_button = ttk.Button(self.button_frame, text="Gravar", command=self.start_recording)
        self.start_button.pack(side='left', padx=10)

        self.stop_button = ttk.Button(self.button_frame, text="Parar", command=self.stop_recording, state='disabled')
        self.stop_button.pack(side='right', padx=10)

        self.fig, self.ax = plt.subplots(figsize=(8, 2), dpi=100)
        self.ax.set_facecolor('#34495e')
        self.fig.patch.set_facecolor('#34495e')
        self.ax.tick_params(colors='white')
        for spine in self.ax.spines.values():
            spine.set_edgecolor('white')
        self.ax.set_title("Gráficos em Tempo Real", color='white')
        self.ax.set_xlabel("Tempo", color='white')
        self.ax.set_ylabel("Amplitude", color='white')
        self.ax.grid(True, color='gray', linestyle='--', linewidth=0.5)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.recording_frame)
        self.canvas.get_tk_widget().grid(row=4, column=0, columnspan=8, pady=20)

    def create_library_widgets(self):
        self.library_title = ttk.Label(self.library_frame, text="Biblioteca de Gravações", font=("Roboto", 24, 'bold'))
        self.library_title.pack(pady=10)

        self.library_list = tk.Listbox(self.library_frame, font=("Roboto", 12), width=50, height=10, bg='#34495e', fg='white')
        self.library_list.pack(pady=10)

        self.refresh_button = ttk.Button(self.library_frame, text="Atualizar Biblioteca", command=self.refresh_library)
        self.refresh_button.pack(pady=10)

    def create_settings_widgets(self):
        self.settings_title = ttk.Label(self.settings_frame, text="Configurações", font=("Roboto", 24, 'bold'))
        self.settings_title.pack(pady=10)

        self.sample_rate_var = tk.IntVar(value=44100)
        self.sample_rate_label = ttk.Label(self.settings_frame, text="Taxa de Amostragem:")
        self.sample_rate_label.pack()
        self.sample_rate_combobox = ttk.Combobox(self.settings_frame, textvariable=self.sample_rate_var, 
                                                 values=[8000, 16000, 44100, 48000, 96000])
        self.sample_rate_combobox.pack()

        self.format_var = tk.StringVar(value="wav")
        self.format_label = ttk.Label(self.settings_frame, text="Formato de Áudio:")
        self.format_label.pack()
        self.format_combobox = ttk.Combobox(self.settings_frame, textvariable=self.format_var, 
                                            values=["wav", "mp3", "flac"])
        self.format_combobox.pack()

        self.save_dir_label = ttk.Label(self.settings_frame, text="Pasta de Salvamento:")
        self.save_dir_label.pack()
        self.save_dir_entry = ttk.Entry(self.settings_frame, width=50)
        self.save_dir_entry.insert(0, self.save_directory)
        self.save_dir_entry.pack()
        self.save_dir_button = ttk.Button(self.settings_frame, text="Escolher Pasta", command=self.choose_save_directory)
        self.save_dir_button.pack()

    def create_about_widgets(self):
        self.about_title = ttk.Label(self.about_frame, text="Sobre o SoundMaster Pro", font=("Roboto", 24, 'bold'))
        self.about_title.pack(pady=10)

        self.version_label = ttk.Label(self.about_frame, text="Versão 1.0.0", font=("Roboto", 14))
        self.version_label.pack()

        self.about_text = tk.Text(self.about_frame, wrap=tk.WORD, width=60, height=10, font=("Roboto", 12), bg='#34495e', fg='white')
        self.about_text.pack(pady=10)
        self.about_text.insert(tk.END, 
            "SoundMaster Pro é uma ferramenta de gravação de áudio de alto nível, desenvolvida com Python e Tkinter. "
            "Com uma gama de recursos profissionais, o SoundMaster Pro permite a visualização em tempo real das gravações, "
            "compatibilidade com múltiplos formatos de áudio e oferece uma interface de usuário clara e acessível.\n\n"
            "Desenvolvido por: Felipe Sinn\n"
            "Contato: felipesinn01@gmail.com"
        )
        self.about_text.config(state=tk.DISABLED)

    def start_recording(self):
        self.recording_event.set()
        self.start_button['state'] = "disabled"
        self.stop_button['state'] = 'normal'
        self.activity_indicator.config(bg='#2ecc71', text='Gravando...')
        
        self.audio_thread = threading.Thread(target=self.record_audio)
        self.audio_thread.start()

        self.timestamp = 0
        self.update_timestamp()

    def stop_recording(self):
        if not self.recording_event.is_set():
            return

        self.recording_event.clear()
        self.start_button['state'] = "normal"
        self.stop_button['state'] = 'disabled'
        self.activity_indicator.config(bg='#e74c3c', text='Gravação parada')

        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join()

        if self.audio_data:
            self.save_recording()
        else:
            messagebox.showwarning("Sem Dados", "Não há dados de áudio para salvar.")

        self.timestamp = 0
        self.audio_data = []

    def record_audio(self):
        chunk_size = 1024
        audio_format = pyaudio.paFloat32
        channels = 1
        rate = self.sample_rate_var.get()

        p = pyaudio.PyAudio()
        try:
            stream = p.open(format=audio_format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk_size)

            self.audio_data = []

            while self.recording_event.is_set():
                data = np.frombuffer(stream.read(chunk_size), dtype=np.float32)
                self.audio_data.extend(data)
        except Exception as e:
            messagebox.showerror("Erro de Gravação", f"Ocorreu um erro durante a gravação: {str(e)}")
        finally:
            if 'stream' in locals():
                stream.stop_stream()
                stream.close()
            p.terminate()

    def save_recording(self):
        if not self.audio_data:
            messagebox.showwarning("Sem Dados", "Não há dados de áudio para salvar.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gravacao_{timestamp}.{self.format_var.get()}"
        
        save_path = filedialog.asksaveasfilename(
            initialdir=self.save_directory,
            defaultextension=f".{self.format_var.get()}", 
            filetypes=[(f"Arquivos {self.format_var.get().upper()}", f"*.{self.format_var.get()}")],
            initialfile=filename
        )
        
        if save_path:
            try:
                sf.write(save_path, np.array(self.audio_data), self.sample_rate_var.get())
                messagebox.showinfo("Sucesso", f"Gravação salva como {save_path}")
                self.refresh_library()
            except Exception as e:
                messagebox.showerror("Erro ao Salvar", f"Ocorreu um erro ao salvar o arquivo: {str(e)}")
        else:
            messagebox.showinfo("Cancelado", "Salvamento cancelado pelo usuário.")

    def update_timestamp(self):
        if self.recording_event.is_set():
            self.timestamp_label["text"] = f"Duração: {self.timestamp / 10.0:.2f} s"
            self.timestamp += 1
            self.master.after(100, self.update_timestamp)

    def update_clock(self):
        if not self.running:
            return
        current_time = datetime.now().strftime("%H:%M:%S")
        self.clock_label.config(text=current_time)
        self.clock_after_id = self.master.after(1000, self.update_clock)

    def update_plot(self):
        if not self.running:
            return
        if self.recording_event.is_set() and self.audio_data:
            data = self.audio_data[-44100:]  # Último segundo de áudio
            self.ax.clear()
            self.ax.plot(data, color='#3498db')
            self.ax.set_ylim(-1, 1)
            self.ax.set_title("Forma de Onda do Áudio em Tempo Real", color='white')
            self.ax.set_xlabel("Amostra", color='white')
            self.ax.set_ylabel("Amplitude", color='white')
            self.ax.tick_params(colors='white')
            self.ax.grid(True, color='gray', linestyle='--', linewidth=0.5)
            self.canvas.draw()
        self.plot_after_id = self.master.after(100, self.update_plot)

    def refresh_library(self):
        self.library_list.delete(0, tk.END)
        for file in os.listdir(self.save_directory):
            if file.endswith(('.wav', '.mp3', '.flac')):
                self.library_list.insert(tk.END, file)

    def choose_save_directory(self):
        new_directory = filedialog.askdirectory()
        if new_directory:
            self.save_directory = new_directory
            self.save_dir_entry.delete(0, tk.END)
            self.save_dir_entry.insert(0, self.save_directory)

    def on_closing(self):
     self.running = False
     self.recording_event.clear()

     if self.audio_thread and self.audio_thread.is_alive():
        self.audio_thread.join()

     if self.plot_after_id:
        self.master.after_cancel(self.plot_after_id)

     if self.clock_after_id:
        self.master.after_cancel(self.clock_after_id)

     self.master.quit()
     self.master.destroy()
    

    def run(self):
        self.update_clock()
        self.update_plot()
        self.master.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = SoundMasterPro(root)
    try:
        app.run()
    except Exception as e:
        print(f"Erro não tratado: {e}")
