import sounddevice as sd
import queue
import numpy as np


class AudioStream:
    """
    Handles real-time microphone input and pushes audio chunks to a queue.
    """

    def __init__(
        self,
        samplerate=16000,
        blocksize=1600,   # 0.1 sec chunks
        channels=1,
        dtype="float32"
    ):
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.channels = channels
        self.dtype = dtype

        self.audio_q = queue.Queue()
        self.stream = None

    # --- INTERNAL CALLBACK ---
    def _callback(self, indata, frames, time, status):
        if status:
            print(f"[AudioStream Warning] {status}")
        # Copy to avoid memory issues
        self.audio_q.put(indata.copy())

    # --- START STREAM ---
    def start(self):
        if self.stream is not None:
            return

        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            channels=self.channels,
            dtype=self.dtype,
            callback=self._callback
        )
        self.stream.start()

    # --- STOP STREAM ---
    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    # --- GET AUDIO CHUNK ---
    def read(self, timeout=None) -> np.ndarray:
        """
        Returns next audio chunk (non-blocking if timeout is set).
        """
        try:
            data = self.audio_q.get(timeout=timeout)
            return data.flatten().astype(np.float32)
        except queue.Empty:
            return None
