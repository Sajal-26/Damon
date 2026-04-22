from pathlib import Path

import config
from senses.vision import (
    CaptureInfo,
    VisionPipeline,
    capture_clipboard,
    capture_screen,
    capture_webcam,
    close_webcam,
    open_webcam,
    record_webcam_frames,
    show_webcam,
)


# from senses import listen, start, stop
# from voice import DamonTTS
#
#
# def voice_main():
#     print("[SYSTEM] Initializing Damon...\n")
#
#     start()
#     tts = DamonTTS()
#
#     print("\n[SYSTEM] Ready. Speak.\n")
#
#     try:
#         while True:
#             result = listen(timeout=0.1)
#
#             if result:
#                 print(f"You said: {result}")
#                 tts.feed(result)
#                 tts.flush()
#
#     except KeyboardInterrupt:
#         stop()
#         print("\n[SYSTEM] Shutting down...")


def _print_capture(label: str, capture: CaptureInfo | None):
    if capture is None:
        print(f"[{label}] No capture returned.")
        return

    print(f"[{label}] kind={capture.kind}")

    if capture.path:
        print(f"[{label}] path={capture.path}")
        print(f"[{label}] exists={Path(capture.path).exists()}")

    if capture.text:
        print(f"[{label}] text={capture.text}")

    if capture.mime_type:
        print(f"[{label}] mime={capture.mime_type}")

    if capture.metadata:
        print(f"[{label}] metadata={capture.metadata}")


def _try(label: str, func, *args, **kwargs):
    print(f"\n[SYSTEM] Checking {label}...")

    try:
        result = func(*args, **kwargs)
    except Exception as exc:
        print(f"[{label}] skipped/error: {exc}")
        return None

    _print_capture(label, result)
    return result


def check_screen():
    return _try("screen capture", capture_screen)


def check_clipboard():
    return _try("clipboard capture", capture_clipboard)


def check_webcam_capture():
    print("\n[SYSTEM] Checking webcam capture...")

    try:
        open_webcam()
        capture = capture_webcam()
    except Exception as exc:
        print(f"[webcam capture] skipped/error: {exc}")
        return None
    finally:
        close_webcam()

    _print_capture("webcam capture", capture)
    return capture


def check_webcam_frames(duration_seconds: float = 30):
    print(f"\n[SYSTEM] Checking adaptive webcam frame capture for {duration_seconds:g}s...")

    try:
        open_webcam()
        capture = record_webcam_frames(
            duration_seconds=duration_seconds,
            save_to_disk=True,
        )
    except Exception as exc:
        print(f"[webcam frames] skipped/error: {exc}")
        return None
    finally:
        close_webcam()

    _print_capture("webcam frames", capture)
    return capture


def check_pipeline():
    print("\n[SYSTEM] Checking async vision pipeline...")
    pipeline = VisionPipeline()

    try:
        pipeline.run(source="screen")
        capture = pipeline.get(timeout=10)
    except Exception as exc:
        print(f"[pipeline] skipped/error: {exc}")
        return None
    finally:
        pipeline.shutdown()

    _print_capture("pipeline", capture)
    return capture


def preview_webcam():
    print("\n[SYSTEM] Opening webcam preview. Press q in the preview window to close.")

    try:
        open_webcam()
        show_webcam()
    except Exception as exc:
        print(f"[webcam preview] skipped/error: {exc}")
    finally:
        close_webcam()


def main():
    print("[SYSTEM] Vision function check")
    print(f"[SYSTEM] Media output folder: {config.VISION_OUTPUT_DIR}")
    print(f"[SYSTEM] Image folder: {config.VISION_IMAGE_DIR}")
    print(f"[SYSTEM] Recording folder: {config.VISION_RECORDING_DIR}")

    checks = {
        "1": ("Screen capture", check_screen),
        "2": ("Clipboard capture", check_clipboard),
        "3": ("Webcam image capture", check_webcam_capture),
        "4": ("Webcam adaptive frame capture", check_webcam_frames),
        "5": ("Async pipeline", check_pipeline),
        "6": ("Webcam preview", preview_webcam),
        "7": ("Run safe checks", run_safe_checks),
        "0": ("Exit", None),
    }

    while True:
        print("\nChoose a function to check:")
        for key, (label, _) in checks.items():
            print(f"{key}. {label}")

        choice = input("> ").strip()

        if choice == "0":
            break

        item = checks.get(choice)
        if item is None:
            print("[SYSTEM] Unknown choice.")
            continue

        _, handler = item
        handler()


def run_safe_checks():
    check_screen()
    check_clipboard()
    check_pipeline()


if __name__ == "__main__":
    main()
