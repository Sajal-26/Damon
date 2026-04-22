import numpy as np
import tensorflow_hub as hub
import csv
from pathlib import Path


class SoundClassifier:
    """
    Handles environmental sound classification using YAMNet.
    """

    def __init__(self, model_path=None):
        print("[Sound] Loading YAMNet...", end="\r")
        self.model = hub.load("https://tfhub.dev/google/yamnet/1")
        self.class_names = self._load_labels()
        print("[Sound] Ready.            ")

        # --- CATEGORY GROUPS ---
        self.piano_classes = [
            "Piano", "Grand piano", "Electric piano",
            "Keyboard (musical)", "Harpsichord", "Organ", "Synthesizer"
        ]

        self.guitar_classes = [
            "Guitar", "Acoustic guitar", "Electric guitar",
            "Plucked string instrument", "Strum", "Bass guitar"
        ]

        self.instruments = {
            "Piano": "Piano", "Grand piano": "Piano",
            "Electric piano": "Piano", "Keyboard (musical)": "Piano",
            "Harpsichord": "Piano", "Organ": "Organ", "Synthesizer": "Piano",

            "Guitar": "Guitar", "Acoustic guitar": "Guitar",
            "Electric guitar": "Guitar", "Plucked string instrument": "Guitar",
            "Strum": "Guitar", "Bass guitar": "Guitar",

            "Violin, fiddle": "Violin", "Cello": "Cello",
            "Harp": "Harp",

            "Drum": "Drums", "Drum kit": "Drums", "Percussion": "Drums",

            "Flute": "Flute", "Saxophone": "Sax", "Trumpet": "Trumpet"
        }

        self.noises = {
            "Laughter": "Laugh", "Giggle": "Laugh",
            "Cough": "Cough", "Sneeze": "Sneeze",
            "Applause": "Applause", "Finger snapping": "Snap",
            "Clapping": "Clap", "Typing": "Typing"
        }

        self.generics = {
            "Music": "Music",
            "Musical instrument": "Music"
        }

    # ========================
    # Load YAMNet Labels
    # ========================
    def _load_labels(self):
        labels = []
        with open(self.model.class_map_path().numpy(), "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                labels.append(row["display_name"])
        return labels

    # ========================
    # Smart Tagging Logic
    # ========================
    def _smart_tag(self, scores, prev=None):
        top5 = np.argsort(scores)[::-1][:5]

        has_piano = any(self.class_names[i] in self.piano_classes for i in top5)
        has_guitar = any(self.class_names[i] in self.guitar_classes for i in top5)

        candidates = []

        for i in top5:
            name = self.class_names[i]
            score = float(scores[i])

            if name in ["Music", "Musical instrument"]:
                score *= 0.3

            if name in self.piano_classes:
                score *= 3.0
            elif name in self.guitar_classes:
                score = score * 0.5 if has_piano else score * 3.0

            candidates.append((name, score))

        candidates.sort(key=lambda x: x[1], reverse=True)

        for name, score in candidates:
            if score < 0.1:
                continue

            if name in self.instruments:
                tag = self.instruments[name]

                if prev == "Piano" and tag == "Guitar" and score < 0.8:
                    return "Piano", score

                return tag, score

            if name in self.noises:
                return self.noises[name], score

        # fallback
        top_name, top_score = candidates[0]
        if top_name in self.generics and top_score > 0.25:
            return self.generics[top_name], top_score

        return None, 0.0

    # ========================
    # Analyze Audio
    # ========================
    def analyze(self, audio: np.ndarray):
        """
        Returns list of detected sound tags from audio.
        """
        if len(audio) < 16000:
            return []

        scores, _, _ = self.model(audio)

        tags = []
        last_tag = None

        for frame in scores.numpy():
            tag, _ = self._smart_tag(frame, last_tag)

            if tag:
                if not tags or tags[-1] != tag:
                    tags.append(tag)

                if tag in ["Piano", "Guitar", "Violin"]:
                    last_tag = tag

        return tags