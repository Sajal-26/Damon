_pipeline = None


def _get_pipeline():
    global _pipeline

    if _pipeline is None:
        from .pipeline import ListeningPipeline

        _pipeline = ListeningPipeline()
        _pipeline.start()

    return _pipeline


def start():
    """
    Start the shared listening pipeline.
    """

    _get_pipeline()


def listen(timeout=None):
    """
    Blocking call that returns the next speech result.
    """

    pipeline = _get_pipeline()
    return pipeline.get(timeout=timeout)


def stop():
    """
    Stop the shared listening pipeline if it is running.
    """

    global _pipeline

    if _pipeline is not None:
        _pipeline.stop()
        _pipeline = None


def __getattr__(name):
    if name == "ListeningPipeline":
        from .pipeline import ListeningPipeline

        return ListeningPipeline
    if name == "STT":
        from .stt import STT

        return STT
    if name == "SoundClassifier":
        from .sound import SoundClassifier

        return SoundClassifier
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "ListeningPipeline",
    "STT",
    "SoundClassifier",
    "listen",
    "start",
    "stop",
]
