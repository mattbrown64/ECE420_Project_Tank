import time
import logging
import importlib

logger = logging.getLogger(__name__)


def _get_gpio_module():
    try:
        return importlib.import_module("RPi.GPIO")
    except ModuleNotFoundError as exc:
        raise RuntimeError("RPi.GPIO is required on Raspberry Pi") from exc


def setup(trigger_pin, forward_pin, left_pin, right_pin):
    GPIO = _get_gpio_module()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(trigger_pin, GPIO.OUT)
    GPIO.setup(forward_pin, GPIO.IN)
    GPIO.setup(left_pin, GPIO.IN)
    GPIO.setup(right_pin, GPIO.IN)
    GPIO.output(trigger_pin, False)


def check_sensor(trigger_pin, sensor_pin):
    GPIO = _get_gpio_module()
    GPIO.output(trigger_pin, True)
    time.sleep(0.00001)
    GPIO.output(trigger_pin, False)

    timeout_start = time.time() + 0.1
    while GPIO.input(sensor_pin) == 0:
        if time.time() > timeout_start:
            logger.warning("Sensor %s: timeout waiting for echo HIGH", sensor_pin)
            return -1

    pulse_start = time.time()

    timeout_end = pulse_start + 0.05
    while GPIO.input(sensor_pin) == 1:
        if time.time() > timeout_end:
            logger.warning("Sensor %s: timeout waiting for echo LOW", sensor_pin)
            return -1

    pulse_end = time.time()

    duration = pulse_end - pulse_start
    distance = (duration * 34300) / 2
    logger.debug(
        "Sensor %s: duration %.6fs, distance %.2f cm",
        sensor_pin,
        duration,
        distance,
    )
    return distance


def cleanup():
    GPIO = _get_gpio_module()
    GPIO.cleanup()
