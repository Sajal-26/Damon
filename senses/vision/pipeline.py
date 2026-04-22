import queue
from concurrent.futures import ThreadPoolExecutor

from .camera import capture_webcam, record_webcam_frames
from .clipboard import capture_clipboard
from .screen import capture_screen
from .types import CaptureInfo


class VisionPipeline:
    def __init__(self, max_workers: int = 2):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.output_q = queue.Queue()

    def capture(self, source: str = "screen", **kwargs) -> CaptureInfo:
        if source == "screen":
            return capture_screen(**kwargs)
        if source == "webcam":
            return capture_webcam(**kwargs)
        if source == "webcam_frames":
            return record_webcam_frames(**kwargs)
        if source == "clipboard":
            return capture_clipboard(**kwargs)
        raise ValueError(f"Unknown vision source: {source}")

    def run(self, source: str = "screen", **capture_kwargs):
        future = self.executor.submit(self.capture, source, **capture_kwargs)
        future.add_done_callback(self.output_q.put)
        return future

    def get(self, timeout=None) -> CaptureInfo | None:
        try:
            future = self.output_q.get(timeout=timeout)
        except queue.Empty:
            return None

        return future.result()

    def shutdown(self):
        self.executor.shutdown(wait=False)
