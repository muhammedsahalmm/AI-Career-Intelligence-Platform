import logging
import sys
from pathlib import Path


# ============================================================
# Log Directory
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

LOG_DIR = BASE_DIR / "logs"

LOG_DIR.mkdir(
    exist_ok=True
)


# ============================================================
# Log File
# ============================================================

LOG_FILE = LOG_DIR / "resume_platform.log"


# ============================================================
# Log Format
# ============================================================

LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# ============================================================
# Application Logger
# ============================================================

logger = logging.getLogger("ai_career_platform")

logger.setLevel(logging.INFO)

# Prevent duplicate handlers when module is re-imported
# (Streamlit reruns the script and re-imports modules)
if not logger.handlers:

    formatter = logging.Formatter(
        LOG_FORMAT,
        datefmt=DATE_FORMAT
    )

    # --------------------------------------------------------
    # File Handler
    # --------------------------------------------------------

    file_handler = logging.FileHandler(
        filename=str(LOG_FILE),
        mode="a",
        encoding="utf-8"
    )

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    # --------------------------------------------------------
    # Console Handler
    # --------------------------------------------------------

    console_handler = logging.StreamHandler(
        sys.stdout
    )

    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)


# Prevent log records from bubbling to the root logger
# (avoids duplicate lines from FastAPI / Streamlit's own loggers)
logger.propagate = False