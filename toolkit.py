import logging
import time
import tomllib
import uuid
from contextlib import contextmanager
from typing import Any, Final

# -----------------------------
# Colour Logging
# -----------------------------


class ColourFormatter(logging.Formatter):

    """Logging Formatter to add colours and count warning / errors"""
    #TODO: Move this to a config file or make it configurable via environment variables
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

class ConfigSettings:
    
    """
    A class to hold configuration settings for the application.
    This can be extended to include more settings as needed.
    """
    def __init__(self, filename: str, log_level: int = logging.DEBUG):
        self.filename = filename
        self.log_level = log_level

    def __str__(self):
        return f"ConfigSettings(filename='{self.filename}', log_level={self.log_level})"


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


def get_logger(name: str|None = None) -> logging.Logger:
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
P        A string representation of a random UUID.
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

class ConfigLoader:
    def __init__(self, filename: str):
        """
        Load configuration settings from a TOML file.

        Args:
            filename (str): Path to the TOML configuration file.
        """

        self.filename: str = filename
        self.config: dict[str, Any] = {}
        try:
            with open(filename, "rb") as f:
                self.config = tomllib.load(f)

            if not self.config:
                raise FileNotFoundError(f"Configuration file '{filename}' is empty.")
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file '{filename}' not found.")
        except tomllib.TOMLDecodeError:
            raise ValueError(f"Invalid configuration file '{filename}'. Expected a valid TOML format, TOMLDecodeError encountered.")


    def __str__(self):
        return f"ConfigLoader(filename='{self.filename}', config={self.config})"

    def __repr__(self):
        return f"ConfigLoader({self.filename!r})"

    def get(self, keys: list[str]) -> str | int | float | bool | dict[str, Any] | None:
        """
        Retrieve a value from the configuration using a list of keys.
        If any key in the list does not exist, return None.

        Args:
            keys (list[str]): A list of keys representing the path to the desired value in the configuration.

        Returns:
            dict[str, Any] | None: The value at the specified path, or None if any key in the path does not exist.

        TOML file example:

        Version = "1.0.0"
        [FS]
        Keyboard = "Chinese"
        Joystick = "HOTAS"
        Speed = "12"
        speed = "22.2"

        useage:

        settings = ConfigLoader("config.toml")
        top_level_value = settings.get(["Version"])
        value = settings.get(["FS", "Keyboard"])
        x = settings.get(["tiger", "Speed"])  # returns None since "tiger" key does not exist
        returns:

        top_level_value: "1.0.0"
        value: "Chinese"
        x: None
        """

        value = self.config

        for key in keys:
            if not isinstance(value, dict):
                return None

            value: str | int | float | bool | dict[str, Any] | None = value.get(key)

            if value is None:
                return None

        return value

    def get_all(self) -> dict[str, str]:
        return self.config