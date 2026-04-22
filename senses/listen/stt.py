import re

from faster_whisper import WhisperModel
from faster_whisper.utils import download_model

import config
from .romanizer import romanize_text


class STT:
    """
    Wrapper for Whisper-based speech-to-text.
    """

    def __init__(self):
        print("[STT] Loading Whisper...", end="\r")

        model_path = download_model(
            config.WHISPER_MODEL,
            output_dir=str(config.WHISPER_MODEL_DIR),
        )

        self.model = WhisperModel(
            model_path,
            device=config.DEVICE,
            compute_type=config.COMPUTE_TYPE,
        )

        # Common hallucinations to ignore
        self.hallucinations = [
            "thank you for watching",
            "thanks for watching",
            "watching!",
            "hause",
            "auf dem",
        ]

        print("[STT] Ready.            ")

    # ========================
    # Transcription
    # ========================
    def transcribe(self, audio):
        """
        Transcribes audio numpy array into text.
        Returns a clean string.
        """

        if audio is None or len(audio) < 8000:
            return ""

        try:
            segments, _ = self.model.transcribe(
                audio,
                beam_size=5,
                language=config.STT_LANGUAGE,
                task="transcribe",
                word_timestamps=True,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
            )

            parts = []

            for seg in segments:
                text = seg.text.strip()
                if config.STT_ROMANIZE:
                    text = romanize_text(text)

                # Clean hallucinations
                cleaned = re.sub(r"[^\w\s]", "", text.lower()).strip()
                if any(h in cleaned for h in self.hallucinations):
                    continue

                if text:
                    parts.append(text)

            return " ".join(parts)

        except Exception as e:
            print(f"[STT Error] {e}")
            return ""
