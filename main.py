import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
import pyaudio
import wave
import threading as th
from datetime import datetime
import os

def start():
    global keep_going
    global temp
    global record_thread

    if not save_directory_var.get():
        messagebox.showwarning("Diretório não selecionado", "Por favor, escolha o diretório de salvamento antes de iniciar a gravação.")
        return

    keep_going = True
    temp = 0
    startButton['state'] = "disabled"
    stopButton['state'] = 'normal'
    updateTimeStamp()
    
    # Change indicator color and text to show recording is active
    activity_indicator.config(bg='green', text='Gravando...')
    
    record_thread = th.Thread(target=gravar, args=(menuTaxaAmostVar.get(),))
    record_thread.start()

def stop():
    global keep_going
    global temp_id
    keep_going = False
    top.after_cancel(temp_id)
    startButton['state'] = "normal"
    stopButton['state'] = 'disabled'
    
    # Change indicator color and text to show recording has stopped
    activity_indicator.config(bg='red', text='Gravação parada')
    
    if record_thread.is_alive():
        record_thread.join()

    messagebox.showinfo("Gravação Encerrada", "A gravação foi salva com sucesso!")

def gravar(rate):
    CHUNK = int(rate / 10)
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = rate
    TIMESTAMP = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

    save_directory = save_directory_var.get()
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    
    WAVE_OUTPUT_FILENAME = os.path.join(save_directory, f"ÁudioPCM_{TIMESTAMP}.wav")

    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        frames = []

        while keep_going:
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro durante a gravação: {e}")

def updateTimeStamp():
    global temp
    global temp_id
    timestamplabel["text"] = f"Duração: {temp / 10.0:.2f} s"
    temp += 1
    temp_id = top.after(100, updateTimeStamp)

def show_about():
    notebook.select(about_frame)

def choose_directory():
    directory = filedialog.askdirectory()
    if directory:
        save_directory_var.set(directory)
        save_directory_label.config(text=f"Diretório de salvamento: {directory}")

top = tk.Tk()
top.title('SoundMaster')
top.geometry('600x400')
top.configure(bg='#e0e0e0')

keep_going = False
record_thread = None

# Style configuration
style = ttk.Style()
style.configure('TButton', font=('Arial', 12), padding=8, relief='flat')
style.configure('TButton', background='#00796B', foreground='white')  # Custom color for buttons
style.map('TButton', background=[('pressed', '#004d40'), ('active', '#004d40')])  # Darker color when pressed or active
style.configure('TLabel', font=('Arial', 12), background='#e0e0e0')
style.configure('TNotebook', background='#e0e0e0')
style.configure('TFrame', background='#e0e0e0')

# Create a notebook
notebook = ttk.Notebook(top)
notebook.pack(pady=20, fill='both', expand=True)

# Create frames for different tabs
recording_frame = ttk.Frame(notebook, padding=20)
about_frame = ttk.Frame(notebook, padding=20)

notebook.add(recording_frame, text='Gravação')
notebook.add(about_frame, text='Sobre')

# Recording tab
menuTaxaAmostList = [8000, 11025, 16000, 22050, 32000, 37800, 44100, 48000, 88200, 96000, 192000]
menuTaxaAmostVar = tk.IntVar(value=menuTaxaAmostList[0])  # Default to the lowest value for smaller file size

freq_scale_label = ttk.Label(recording_frame, text="Taxa de Amostragem [Hz]:")
freq_scale_label.grid(row=1, column=0, padx=10, pady=10, sticky='w')

freq_scale = tk.Scale(recording_frame, from_=menuTaxaAmostList[0], to=menuTaxaAmostList[-1], orient='horizontal', resolution=100, length=300, variable=menuTaxaAmostVar)
freq_scale.grid(row=1, column=1, padx=10, pady=10, sticky='ew')

startButton = ttk.Button(recording_frame, text="Gravar", command=start)
startButton.grid(row=2, column=0, pady=20, padx=10, sticky='ew')

stopButton = ttk.Button(recording_frame, text="Parar", state=tk.DISABLED, command=stop)
stopButton.grid(row=2, column=1, pady=20, padx=10, sticky='ew')

titulo_aplicacao = ttk.Label(recording_frame, text="SoundMaster", font=("Arial", 24, 'bold'))
titulo_aplicacao.grid(row=0, column=0, columnspan=2, pady=10)

instrucoes = ttk.Label(recording_frame, text="Aperte 'Gravar' para iniciar a gravação\nAperte 'Parar' para salvar e encerrar a gravação\nEscolha a Taxa de Amostragem na barra abaixo", justify='center')
instrucoes.grid(row=1, column=0, columnspan=2, pady=10)

temp = 0
temp_id = None
timestamplabel = ttk.Label(recording_frame, text="Duração")
timestamplabel.grid(row=3, column=0, columnspan=2, pady=10)

# Activity Indicator
activity_indicator = tk.Label(recording_frame, text="Inativo", bg='red', fg='white', font=("Arial", 16), width=20, height=2, anchor='center')
activity_indicator.grid(row=4, column=0, columnspan=2, pady=20)

# Directory selection
save_directory_var = tk.StringVar()
directory_button = ttk.Button(recording_frame, text="Escolher Diretório", command=choose_directory)
directory_button.grid(row=5, column=0, columnspan=2, pady=10)

save_directory_label = ttk.Label(recording_frame, text="Diretório de salvamento: Nenhum")
save_directory_label.grid(row=6, column=0, columnspan=2, pady=10)

# Adjust column weights for better alignment
recording_frame.grid_columnconfigure(0, weight=1)
recording_frame.grid_columnconfigure(1, weight=1)

# About tab
about_title = ttk.Label(about_frame, text="Sobre o SoundMaster", font=("Arial", 24, 'bold'))
about_title.pack(pady=20)

version_info = ttk.Label(about_frame, text="Versão 1.0", font=("Arial", 14))
version_info.pack(pady=5)

info_message = ttk.Label(about_frame, text="Desenvolvido para atender a necessidade de gravar áudio de alta qualidade pensando no cliente final.", font=("Arial", 12), wraplength=500, justify='center')
info_message.pack(pady=10)

developer_info = ttk.Label(about_frame, text="Desenvolvido por Felipe Sinn", font=("Arial", 12))
developer_info.pack(pady=30)

# Add an About button to the menu bar
menubar = tk.Menu(top)
top.config(menu=menubar)
help_menu = tk.Menu(menubar, tearoff=0)
help_menu.add_command(label="Sobre", command=show_about)
menubar.add_cascade(label="Ajuda", menu=help_menu)

top.mainloop()
