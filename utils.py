import io
import logging
import os

logger = logging.getLogger(__name__)
_LOGGING_CONFIGURED = False


def configure_logging(level=None, log_file=None):
    """Configure application-wide logging once."""
    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return

    log_level_name = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=handlers,
    )
    _LOGGING_CONFIGURED = True

def is_raspberry_pi():
    """Checks if the code is running on a Raspberry Pi."""
    logger.debug("Checking if running on Raspberry Pi")
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower():
                logger.info("Detected Raspberry Pi")
                return True
    except FileNotFoundError:
        logger.debug("Device tree model file not found, not running on Raspberry Pi")
    logger.debug("Not running on Raspberry Pi")
    return False