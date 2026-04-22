import config as config


def __getattr__(name):
    if name == "DamonTTS":
        from .tts import DamonTTS

        return DamonTTS
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["DamonTTS", "config"]
