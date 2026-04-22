import re

class TextChunker:
    def __init__(self):
        self.buffer = ""

    def feed(self, text):
        self.buffer += " " + text
        words = self.buffer.strip().split()

        chunks = []

        while len(words) >= 10:
            split_index = None

            for i in range(10, len(words)):
                if re.search(r'[.?!]$', words[i]):
                    split_index = i
                    break

            if split_index is None:
                break

            remaining = len(words) - (split_index + 1)

            if remaining <= 5:
                split_index = len(words) - 1

            sentence = " ".join(words[:split_index + 1])
            chunks.append(sentence)

            words = words[split_index + 1:]
            self.buffer = " ".join(words)

        return chunks

    def flush(self):
        if self.buffer.strip():
            remaining = self.buffer.strip()
            self.buffer = ""
            return [remaining]
        return []