import logging

logger = logging.getLogger(__name__)


_default_distance_cm = 100.0


def setup(trigger_pin, forward_pin, left_pin, right_pin):
    logger.info(
        "Using mock GPIO backend (trigger=%s, forward=%s, left=%s, right=%s)",
        trigger_pin,
        forward_pin,
        left_pin,
        right_pin,
    )


def check_sensor(trigger_pin, sensor_pin):
    logger.debug(
        "Mock sensor read for trigger %s, sensor %s -> %.2f cm",
        trigger_pin,
        sensor_pin,
        _default_distance_cm,
    )
    return _default_distance_cm


def cleanup():
    logger.info("Mock GPIO cleanup complete")
