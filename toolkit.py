import time
import logging
import uuid
from typing import Final, Optional
from contextlib import contextmanager

# -----------------------------
# Colour Logging
# -----------------------------


class ColourFormatter(logging.Formatter):
    COLOURS = {
        logging.DEBUG: "\033[36m",  # Cyan
        logging.INFO: "\033[38;5;46m",  # Bright neon lime green
        logging.WARNING: "\033[38;5;226m",  # Pure neon yellow (very bright)
        logging.ERROR: "\033[38;5;214m",  # Light Orange (ANSI 214)
        logging.CRITICAL: "\033[38;5;197m",  # Bright Magenta/Red
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        colour = self.COLOURS.get(record.levelno, self.RESET)
        message = super().format(record)
        return f"{colour}{message}{self.RESET}"


def setup_logging(level: int = logging.DEBUG) -> None:
    """
    Initialise colour logging for the entire application.
    Call this once at program startup.
    """
    handler = logging.StreamHandler()

    fmt = (
        "%(asctime)sZ "
        "[%(levelname)s] "
        "%(threadName)s "
        "%(module)s.%(funcName)s:%(lineno)d -> "
        "%(message)s"
    )

    datefmt = "%Y-%m-%dT%H:%M:%S"

    formatter = ColourFormatter(fmt, datefmt=datefmt)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Retrieve a logger for a module or component.
    """
    return logging.getLogger(name)


# -----------------------------
# UUID Utilities
# -----------------------------

UUID_VERSION: Final[int] = 4


def new_uuid() -> str:
    """
    Generate a new UUID string using uuid4().

    Returns:
        A string representation of a random UUID.
    """
    return str(uuid.uuid4())


def short_uuid() -> str:
    """
    Generate a shorter, URL‑safe UUID-like identifier.
    Not a real UUID, but useful for filenames or compact IDs.

    Returns:
        A 12‑character shortened identifier.
    """
    return uuid.uuid4().hex[:12]


def uuid1_timestamp() -> str:
    """
    Generate a UUID1 (time‑based) and return it as a string.

    Returns:
        A string representation of a time‑based UUID.
    """
    return str(uuid.uuid1())


@contextmanager
def timed(label: str):
    # Call like this:
    # with timed("Function time"):
    #    run_event_loop()
    #
    # Starts timer
    # yeilds to run "run_event_loop()"
    # then continutes finally block, once "run_event_loop()" completes

    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()
        elapsed = (end - start) * 1000
        print(f"{label}: {elapsed:.2f} ms")
