import mimetypes
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class CaptureInfo:
    kind: str
    path: Path | None = None
    text: str | None = None
    mime_type: str | None = None
    metadata: dict = field(default_factory=dict)
    frames: tuple | None = field(default=None, repr=False)


def file_info(path: str | Path, kind: str, metadata: dict | None = None) -> CaptureInfo:
    resolved = Path(path).resolve()
    mime_type, _ = mimetypes.guess_type(resolved)
    return CaptureInfo(
        kind=kind,
        path=resolved,
        mime_type=mime_type,
        metadata=metadata or {},
    )


def text_info(text: str, metadata: dict | None = None) -> CaptureInfo:
    return CaptureInfo(
        kind="text",
        text=text,
        mime_type="text/plain",
        metadata=metadata or {},
    )


def get_prompt_frames(capture: CaptureInfo, limit: int = 10) -> tuple:
    if not capture.frames:
        return ()

    if limit <= 0:
        return ()

    return tuple(capture.frames[-limit:])
