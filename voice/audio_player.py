import numpy as np
import sounddevice as sd
import threading

class AudioPlayer:
    def __init__(self, sample_rate=48000):
        self.sample_rate = sample_rate
        self.buffer = np.zeros(0, dtype=np.float32)
        self.lock = threading.Lock()
        self.is_playing = False

        self.stream = sd.OutputStream(
            samplerate=sample_rate,
            channels=1,
            dtype="float32",
            blocksize=512,
            callback=self._callback
        )
        self.stream.start()

    def _callback(self, outdata, frames, time_info, status):
        with self.lock:
            valid = min(len(self.buffer), frames)

            if valid > 0:
                outdata[:valid, 0] = self.buffer[:valid]
                self.buffer = self.buffer[valid:]
                self.is_playing = True
            else:
                self.is_playing = False

            if valid < frames:
                outdata[valid:, 0] = 0.0

    def write(self, audio_data):
        audio_data = audio_data.astype(np.float32).flatten()
        padding = np.zeros(2000, dtype=np.float32)
        audio_data = np.concatenate([audio_data, padding])

        with self.lock:
            self.buffer = np.concatenate((self.buffer, audio_data))

    def close(self):
        self.stream.stop()
        self.stream.close()