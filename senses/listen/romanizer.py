import re


INDEPENDENT_VOWELS = {
    "अ": "a",
    "आ": "aa",
    "इ": "i",
    "ई": "ee",
    "उ": "u",
    "ऊ": "oo",
    "ऋ": "ri",
    "ए": "e",
    "ऐ": "ai",
    "ओ": "o",
    "औ": "au",
}

VOWEL_SIGNS = {
    "ा": "aa",
    "ि": "i",
    "ी": "ee",
    "ु": "u",
    "ू": "oo",
    "ृ": "ri",
    "े": "e",
    "ै": "ai",
    "ो": "o",
    "ौ": "au",
}

CONSONANTS = {
    "क": "k",
    "ख": "kh",
    "ग": "g",
    "घ": "gh",
    "ङ": "ng",
    "च": "ch",
    "छ": "chh",
    "ज": "j",
    "झ": "jh",
    "ञ": "ny",
    "ट": "t",
    "ठ": "th",
    "ड": "d",
    "ढ": "dh",
    "ण": "n",
    "त": "t",
    "थ": "th",
    "द": "d",
    "ध": "dh",
    "न": "n",
    "प": "p",
    "फ": "ph",
    "ब": "b",
    "भ": "bh",
    "म": "m",
    "य": "y",
    "र": "r",
    "ल": "l",
    "व": "v",
    "श": "sh",
    "ष": "sh",
    "स": "s",
    "ह": "h",
    "ळ": "l",
}

NUKTA_CONSONANTS = {
    "क": "q",
    "ख": "kh",
    "ग": "gh",
    "ज": "z",
    "ड": "r",
    "ढ": "rh",
    "फ": "f",
    "य": "y",
}

MARKS = {
    "ं": "n",
    "ँ": "n",
    "ः": "h",
}

VIRAMA = "्"
NUKTA = "़"
DEVANAGARI_RE = re.compile(r"[\u0900-\u097f]")


def romanize_text(text: str) -> str:
    if not text or not DEVANAGARI_RE.search(text):
        return text

    romanized = []
    word = []

    def flush_word():
        if not word:
            return

        token = "".join(word)
        if len(token) > 1 and token.endswith("a"):
            token = token[:-1]
        romanized.append(token)
        word.clear()

    i = 0
    while i < len(text):
        char = text[i]
        next_char = text[i + 1] if i + 1 < len(text) else ""
        after_next = text[i + 2] if i + 2 < len(text) else ""

        if char in INDEPENDENT_VOWELS:
            word.append(INDEPENDENT_VOWELS[char])
        elif char in CONSONANTS:
            base = NUKTA_CONSONANTS.get(char, CONSONANTS[char]) if next_char == NUKTA else CONSONANTS[char]
            lookahead = after_next if next_char == NUKTA else next_char

            word.append(base)
            if lookahead not in VOWEL_SIGNS and lookahead != VIRAMA:
                word.append("a")

            if next_char == NUKTA:
                i += 1
        elif char in VOWEL_SIGNS:
            word.append(VOWEL_SIGNS[char])
        elif char in MARKS:
            word.append(MARKS[char])
        elif char == VIRAMA or char == NUKTA:
            pass
        else:
            flush_word()
            romanized.append(char)

        i += 1

    flush_word()

    result = "".join(romanized)
    return _clean_romanized(result)


def _clean_romanized(text: str) -> str:
    text = re.sub(r"\baa", "aa", text)
    text = re.sub(r"\s+", " ", text).strip()
    if text:
        text = text[0].upper() + text[1:]
    return text
