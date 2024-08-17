# recorder.py
import pyaudio
import wave

class AudioRecorder:
    def __init__(self, device_index, rate=44100, channels=1, chunk_size=1024):
        self.device_index = device_index
        self.rate = rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.frames = []
        self.recording = False
        self.pyaudio_instance = pyaudio.PyAudio()

    def start_recording(self):
        self.frames = []
        self.recording = True
        self.stream = self.pyaudio_instance.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.rate,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=self.chunk_size
        )
        self._record()

    def _record(self):
        while self.recording:
            data = self.stream.read(self.chunk_size)
            self.frames.append(data)

    def stop_recording(self):
        self.recording = False
        self.stream.stop_stream()
        self.stream.close()
        self.pyaudio_instance.terminate()

        self.save_recording()

    def save_recording(self):
        filename = "recording.wav"
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.pyaudio_instance.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
        print(f"Recording saved as {filename}")

    def get_device_info(self):
        return self.pyaudio_instance.get_device_info_by_index(self.device_index)
