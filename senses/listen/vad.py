import time
import numpy as np

import config


class VoiceActivityDetector:
    """
    Handles silence detection and converts audio chunks into meaningful segments.
    """

    def __init__(
        self,
        silence_threshold=config.SILENCE_THRESHOLD,
        min_recording_length=config.MIN_RECORDING_LENGTH,
        max_silence_duration=1.0,
    ):
        self.silence_threshold = silence_threshold
        self.min_recording_length = min_recording_length
        self.max_silence_duration = max_silence_duration

        self.buffer = []
        self.recording = False
        self.silence_start = None

    # ========================
    # Process incoming chunk
    # ========================
    def process(self, chunk: np.ndarray):
        """
        Takes a chunk of audio and returns a full segment when speech ends.
        Otherwise returns None.
        """

        if chunk is None or len(chunk) == 0:
            return None

        amplitude = np.max(np.abs(chunk))

        # --- Voice detected ---
        if amplitude > self.silence_threshold:
            if not self.recording:
                self.recording = True

            self.buffer.append(chunk)
            self.silence_start = None
            return None

        # --- Silence detected ---
        if self.recording:
            self.buffer.append(chunk)

            if self.silence_start is None:
                self.silence_start = time.time()

            elif time.time() - self.silence_start > self.max_silence_duration:
                segment = self._finalize()
                return segment

        return None

    # ========================
    # Finalize segment
    # ========================
    def _finalize(self):
        """
        Converts buffer into a single audio segment and resets state.
        """

        if not self.buffer:
            return None

        full_audio = np.concatenate(self.buffer)

        # Reset state
        self.buffer = []
        self.recording = False
        self.silence_start = None

        # Drop too-short clips
        duration = len(full_audio) / 16000.0
        if duration < self.min_recording_length:
            return None

        return full_audio.astype(np.float32)