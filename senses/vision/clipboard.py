from datetime import datetime
from pathlib import Path

import config
from .types import CaptureInfo, file_info, text_info


def _output_path(path: str | Path | None) -> Path:
    if path is not None:
        output = Path(path)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = config.VISION_IMAGE_DIR / f"clipboard_{timestamp}.png"

    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def capture_clipboard(output_path: str | Path | None = None) -> CaptureInfo:
    try:
        from PIL import Image, ImageGrab
    except ImportError as exc:
        raise RuntimeError("Pillow is required for clipboard image capture. Install pillow.") from exc

    clipboard = ImageGrab.grabclipboard()

    if isinstance(clipboard, Image.Image):
        output = _output_path(output_path)
        clipboard.save(output)
        return file_info(output, kind="image")

    if isinstance(clipboard, list) and clipboard:
        return file_info(clipboard[0], kind="file")

    try:
        import pyperclip
    except ImportError as exc:
        raise RuntimeError("pyperclip is required for clipboard text capture. Install pyperclip.") from exc

    return text_info(pyperclip.paste())
