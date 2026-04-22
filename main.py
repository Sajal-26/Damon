from senses import listen, start, stop
from voice import DamonTTS


def main():
    print("[SYSTEM] Initializing Damon...\n")

    # Init systems
    start()
    tts = DamonTTS()

    print("\n[SYSTEM] Ready. Speak.\n")

    try:
        while True:
            result = listen(timeout=0.1)

            if result:
                print(f"You said: {result}")

                # Feed to TTS
                tts.feed(result)
                tts.flush()

    except KeyboardInterrupt:
        stop()
        print("\n[SYSTEM] Shutting down...")


if __name__ == "__main__":
    main()