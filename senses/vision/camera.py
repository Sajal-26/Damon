from collections import deque
from datetime import datetime
import os
from pathlib import Path
from time import monotonic, sleep

import config
from .types import CaptureInfo, file_info


camera = None


def _cv2():
    os.environ["OPENCV_LOG_LEVEL"] = "SILENT"

    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("OpenCV is required for camera features. Install opencv-python.") from exc

    try:
        cv2.setLogLevel(0)
    except AttributeError:
        pass

    return cv2


def _output_path(path: str | Path | None, suffix: str) -> Path:
    if path is not None:
        output = Path(path)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = config.VISION_IMAGE_DIR / f"webcam_{timestamp}{suffix}"

    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def _recording_dir(path: str | Path | None) -> Path:
    if path is not None:
        output = Path(path)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = config.VISION_RECORDING_DIR / f"webcam_frames_{timestamp}"

    output.mkdir(parents=True, exist_ok=True)
    return output


def open_webcam(camera_index: int = 0):
    global camera

    if camera is not None and camera.isOpened():
        return

    cv2 = _cv2()
    backend = cv2.CAP_DSHOW if os.name == "nt" else 0
    camera = cv2.VideoCapture(camera_index, backend)

    if not camera.isOpened():
        camera = None
        raise RuntimeError(f"Cannot open webcam at index {camera_index}")


def close_webcam():
    global camera

    if camera is not None:
        camera.release()
        camera = None


def show_webcam(window_name: str = "Webcam Feed"):
    global camera

    cv2 = _cv2()
    if camera is None or not camera.isOpened():
        raise RuntimeError("Webcam is not open. Call open_webcam() first.")

    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                raise RuntimeError("Error capturing webcam frame")

            cv2.imshow(window_name, frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cv2.destroyAllWindows()


def capture_webcam(output_path: str | Path | None = None) -> CaptureInfo:
    global camera

    cv2 = _cv2()
    if camera is None or not camera.isOpened():
        raise RuntimeError("Webcam is not open. Call open_webcam() first.")

    ok, frame = camera.read()
    if not ok:
        raise RuntimeError("Error capturing webcam frame")

    output = _output_path(output_path, ".jpg")
    if not cv2.imwrite(str(output), frame):
        raise RuntimeError(f"Could not save webcam capture to {output}")

    return file_info(output, kind="image", metadata={"source": "webcam"})


def record_webcam_frames(
    duration_seconds: float,
    output_dir: str | Path | None = None,
    detection_fps: float = 30.0,
    motion_save_fps: float = 5.0,
    still_save_fps: float = 0.2,
    frame_size: tuple[int, int] = (640, 480),
    motion_threshold: float = 2.0,
    save_to_disk: bool = False,
    keep_saved_frames: bool = True,
    recent_buffer_size: int = 10,
    max_selected_frames: int = 50,
    memory_frame_size: tuple[int, int] = (224, 224),
) -> CaptureInfo:
    global camera

    cv2 = _cv2()
    if camera is None or not camera.isOpened():
        raise RuntimeError("Webcam is not open. Call open_webcam() first.")

    output = _recording_dir(output_dir) if save_to_disk else None
    frame_interval = 1.0 / detection_fps
    last_selected_at = 0.0
    last_mode = None
    previous_gray = None
    selected_count = 0
    saved_count = 0
    motion_events = []
    recent_frames = deque(maxlen=recent_buffer_size)
    selected_frames = deque(maxlen=max_selected_frames)

    start_time = monotonic()
    next_frame_at = start_time

    while monotonic() - start_time < duration_seconds:
        now = monotonic()
        if now < next_frame_at:
            sleep(next_frame_at - now)
        next_frame_at += frame_interval

        ok, frame = camera.read()
        if not ok:
            raise RuntimeError("Error capturing webcam frame")

        frame = cv2.resize(frame, frame_size)
        elapsed = monotonic() - start_time
        memory_frame = cv2.resize(frame, memory_frame_size)
        recent_frames.append(memory_frame.copy())

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        motion_detected = False
        motion_score = 0.0
        if previous_gray is not None:
            diff = cv2.absdiff(previous_gray, gray)
            _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
            motion_score = (cv2.countNonZero(thresh) / thresh.size) * 100
            motion_detected = motion_score >= motion_threshold

        previous_gray = gray

        save_fps = motion_save_fps if motion_detected else still_save_fps
        mode = "motion" if motion_detected else "still"

        if mode != last_mode:
            if motion_detected:
                print(f"Motion detected - {motion_save_fps:g} FPS")
            else:
                print(f"{still_save_fps:g} FPS")
            motion_events.append(
                {
                    "time_seconds": round(elapsed, 3),
                    "motion_detected": motion_detected,
                    "mode": mode,
                    "motion_score": round(motion_score, 3),
                    "save_fps": save_fps,
                }
            )
            last_mode = mode

        save_interval = 1.0 / save_fps
        if now - last_selected_at >= save_interval:
            selected_count += 1

            if keep_saved_frames:
                selected_frames.append(memory_frame.copy())

            if save_to_disk:
                saved_count += 1
                frame_path = output / f"frame_{saved_count:06d}.jpg"
                if not cv2.imwrite(str(frame_path), frame):
                    raise RuntimeError(f"Could not save webcam frame to {frame_path}")

            last_selected_at = now

    return CaptureInfo(
        kind="frames",
        path=output.resolve() if output is not None else None,
        mime_type=None,
        metadata={
            "source": "webcam",
            "duration_seconds": duration_seconds,
            "detection_fps": detection_fps,
            "motion_save_fps": motion_save_fps,
            "still_save_fps": still_save_fps,
            "frame_size": frame_size,
            "motion_threshold": motion_threshold,
            "motion_detection": "global_frame_difference",
            "save_to_disk": save_to_disk,
            "selected_frames": selected_count,
            "saved_frames": saved_count,
            "recent_frames": len(recent_frames),
            "memory_frame_size": memory_frame_size,
            "max_selected_frames": max_selected_frames,
            "buffered_frames": len(selected_frames or recent_frames),
            "motion_events": motion_events,
        },
        frames=tuple(selected_frames or recent_frames) or None,
    )
