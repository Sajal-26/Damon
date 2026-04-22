import logging
import os
import warnings
from pathlib import Path


# --- 1. DYNAMIC PATH DETECTION ---
CONFIG_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CONFIG_DIR.parent


# --- 2. LINK DLLS SILENTLY ---
VENV_DIR = PROJECT_ROOT / ".myvenv"
if not VENV_DIR.exists():
    VENV_DIR = PROJECT_ROOT / ".venv"

SITE_PACKAGES = VENV_DIR / "Lib" / "site-packages"

NVIDIA_PATHS = [
    SITE_PACKAGES / "nvidia" / "cudnn" / "bin",
    SITE_PACKAGES / "nvidia" / "cublas" / "bin",
    SITE_PACKAGES / "nvidia" / "cuda_runtime" / "bin",
]

for path in NVIDIA_PATHS:
    if path.exists():
        try:
            os.add_dll_directory(str(path))
            os.environ["PATH"] = str(path) + os.pathsep + os.environ.get("PATH", "")
        except Exception:
            pass


# --- 3. DYNAMIC MODEL PATHS ---
MODELS_DIR = PROJECT_ROOT / "Models"
DATA_DIR = PROJECT_ROOT / "data"
MEDIA_DIR = PROJECT_ROOT / "media"
VISION_OUTPUT_DIR = MEDIA_DIR / "vision"
VISION_IMAGE_DIR = VISION_OUTPUT_DIR / "images"
VISION_RECORDING_DIR = VISION_OUTPUT_DIR / "recordings"
WHISPER_DIR = MODELS_DIR / "whisper"
WHISPER_MODEL = "large-v3"
WHISPER_MODEL_DIR = WHISPER_DIR / WHISPER_MODEL
STT_ROMANIZE = True
STT_LANGUAGE = None
YAMNET_PATH = MODELS_DIR / "tfhub"
HF_HOME = MODELS_DIR / "huggingface"
TORCH_HOME = MODELS_DIR / "torch"

for path in (
    MODELS_DIR,
    DATA_DIR,
    MEDIA_DIR,
    VISION_OUTPUT_DIR,
    VISION_IMAGE_DIR,
    VISION_RECORDING_DIR,
    WHISPER_DIR,
    WHISPER_MODEL_DIR,
    YAMNET_PATH,
    HF_HOME,
    TORCH_HOME,
):
    path.mkdir(parents=True, exist_ok=True)


# --- 4. SYSTEM CONFIGS (SILENT) ---
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TFHUB_CACHE_DIR"] = str(YAMNET_PATH)
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["CT2_CUDA_ALLOW_DLOPEN"] = "1"
os.environ["CT2_VERBOSE"] = "0"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["OPENCV_LOG_LEVEL"] = "SILENT"

warnings.filterwarnings("ignore")
logging.getLogger("faster_whisper").setLevel(logging.ERROR)
logging.getLogger("tensorflow").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("zipvoice").setLevel(logging.ERROR)


# --- 5. MODEL CACHES (FORCE MODELS DIR) ---
os.environ["HF_HOME"] = str(HF_HOME)
os.environ["HF_HUB_CACHE"] = str(HF_HOME / "hub")
os.environ["HUGGINGFACE_HUB_CACHE"] = str(HF_HOME / "hub")
os.environ["TRANSFORMERS_CACHE"] = str(HF_HOME / "transformers")
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TORCH_HOME"] = str(TORCH_HOME)


# --- 6. VOICE / TTS CONFIG ---
DEVICE = "cuda"
COMPUTE_TYPE = "int8_float16"
# DEVICE = "cpu"
# COMPUTE_TYPE = "int8"
SILENCE_THRESHOLD = 0.03
MIN_RECORDING_LENGTH = 0.5
MAX_SILENCE_DURATION = 1.0

TTS_CONFIG = {
    "num_steps": 6,
    "t_shift": 0.85,
    "speed": 1.0,
    "sample_rate": 48000,
}
