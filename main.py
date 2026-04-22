from voice import DamonTTS

tts = DamonTTS()

while True:
    text = input("Input: ")
    tts.feed(text)
    tts.flush()