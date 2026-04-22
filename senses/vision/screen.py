from datetime import datetime
from pathlib import Path

import config
from .types import CaptureInfo, file_info


def _output_path(path: str | Path | None) -> Path:
    if path is not None:
        output = Path(path)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = config.VISION_IMAGE_DIR / f"screen_{timestamp}.png"

    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def capture_screen(output_path: str | Path | None = None, all_screens: bool = True) -> CaptureInfo:
    try:
        from PIL import ImageGrab
    except ImportError as exc:
        raise RuntimeError("Pillow is required for screen capture. Install pillow.") from exc

    output = _output_path(output_path)
    screenshot = ImageGrab.grab(all_screens=all_screens)
    screenshot.save(output)
    return file_info(output, kind="screen", metadata={"all_screens": all_screens})
