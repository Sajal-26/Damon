import queue
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from config import TTS_CONFIG, DEVICE

import torch
from zipvoice.luxvoice import LuxTTS
from .audio_player import AudioPlayer
from .chunker import TextChunker


class DamonTTS:
    def __init__(self, voice_path = None):
        self.device = DEVICE if DEVICE == "cuda" and torch.cuda.is_available() else "cpu"
        print(f"Loading LuxTTS on {self.device}...")

        self.lux = LuxTTS("YatharthS/LuxTTS", device=self.device)

        if voice_path is None:
            base_dir = Path(__file__).parent
            voice_path = base_dir / "Damon_voice.wav"
        
        voice_path = str(voice_path)
        print(f"Using voice sample: {voice_path}")

        print("Encoding voice sample...")
        self.encoded_prompt = self.lux.encode_prompt(
            voice_path,
            duration=6,
            rms=0.1
        )

        self.executor = ThreadPoolExecutor(max_workers=2)
        self.playback_queue = queue.Queue()

        self.audio = AudioPlayer(TTS_CONFIG["sample_rate"])
        self.chunker = TextChunker()

        self.sequencer_thread = threading.Thread(
            target=self._sequencer_loop,
            daemon=True
        )
        self.sequencer_thread.start()

        print("TTS system ready.")

    def _generate_audio(self, text):
        try:
            cfg = TTS_CONFIG

            audio = self.lux.generate_speech(
                text,
                self.encoded_prompt,
                num_steps=cfg["num_steps"],
                t_shift=cfg["t_shift"],
                speed=cfg["speed"],
                return_smooth=True
            )
            return audio.cpu().numpy().squeeze()

        except Exception as e:
            print(f"Error: {e}")
            return None

    def _sequencer_loop(self):
        while True:
            future = self.playback_queue.get()
            if future is None:
                break

            audio_data = future.result()

            if audio_data is not None:
                self.audio.write(audio_data)

            self.playback_queue.task_done()

    def feed(self, text):
        chunks = self.chunker.feed(text)

        for chunk in chunks:
            future = self.executor.submit(self._generate_audio, chunk)
            self.playback_queue.put(future)

    def flush(self):
        chunks = self.chunker.flush()

        for chunk in chunks:
            future = self.executor.submit(self._generate_audio, chunk)
            self.playback_queue.put(future)

    def wait(self):
        self.playback_queue.join()

    def shutdown(self):
        self.playback_queue.put(None)
        self.sequencer_thread.join()
        self.executor.shutdown(wait=False)
        self.audio.close()
