from .camera import (
    capture_webcam,
    close_webcam,
    get_camera_index,
    list_cameras,
    open_webcam,
    record_webcam_frames,
    set_camera_index,
    show_webcam,
)
from .clipboard import capture_clipboard
from .pipeline import VisionPipeline
from .screen import capture_screen
from .types import CaptureInfo, file_info, get_prompt_frames, text_info


__all__ = [
    "CaptureInfo",
    "VisionPipeline",
    "capture_clipboard",
    "capture_screen",
    "capture_webcam",
    "close_webcam",
    "get_camera_index",
    "list_cameras",
    "open_webcam",
    "record_webcam_frames",
    "set_camera_index",
    "show_webcam",
    "file_info",
    "get_prompt_frames",
    "text_info",
]
