import threading
import queue
import time
import numpy as np

from .audio_stream import AudioStream
from .vad import VoiceActivityDetector
from .stt import STT
from .sound import SoundClassifier


class ListeningPipeline:
    """
    Core orchestrator for Damon hearing system.
    """

    def __init__(self):
        # --- Modules ---
        self.stream = AudioStream()
        self.vad = VoiceActivityDetector()
        self.stt = STT()
        self.sound = SoundClassifier()

        # --- Queues ---
        self.process_q = queue.Queue()
        self.output_q = queue.Queue()

        # --- State ---
        self.is_running = False

    # ========================
    # Listener Thread
    # ========================
    def _listener_loop(self):
        while self.is_running:
            chunk = self.stream.read(timeout=0.1)
            if chunk is None:
                continue

            was_recording = self.vad.recording
            segment = self.vad.process(chunk)

            if not was_recording and self.vad.recording:
                print("[SYSTEM] Listening...")

            if segment is not None:
                print("[SYSTEM] Processing...")
                self.process_q.put(segment)

    # ========================
    # Processor Thread
    # ========================
    def _processor_loop(self):
        while self.is_running:
            try:
                audio = self.process_q.get(timeout=1)

                text = self.stt.transcribe(audio)
                sound_events = self.sound.analyze(audio)
                result = self._merge(text, sound_events)

                if result.strip():
                    self.output_q.put(result)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"[Pipeline Error] {e}")

    # ========================
    # Merge Logic
    # ========================
    def _merge(self, text, sound_events):
        """
        Combine speech + sound into a readable format.
        """
        parts = []

        if sound_events:
            for s in sound_events:
                parts.append(f"[{s}]")

        if text:
            parts.append(text)

        return " ".join(parts)

    # ========================
    # Start / Stop
    # ========================
    def start(self):
        if self.is_running:
            return

        self.is_running = True

        self.stream.start()

        threading.Thread(target=self._listener_loop, daemon=True).start()
        threading.Thread(target=self._processor_loop, daemon=True).start()

    def stop(self):
        self.is_running = False
        self.stream.stop()

    # ========================
    # Public API
    # ========================
    def get(self, timeout=None):
        """
        Get processed output (text + sound)
        """
        try:
            return self.output_q.get(timeout=timeout)
        except queue.Empty:
            return None
