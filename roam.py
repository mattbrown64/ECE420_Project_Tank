import logging
from utils import configure_logging
from utils import is_raspberry_pi
import time

logger = logging.getLogger(__name__)

DEFAULT_THRESHOLD_DISTANCE = 5
DEFAULT_SENSOR_FORWARD_PIN = 17
DEFAULT_SENSOR_LEFT_PIN = 27
DEFAULT_SENSOR_RIGHT_PIN = 22
DEFAULT_TRIGGER_PIN = 18

if is_raspberry_pi():
    from gpio_pi_backend import setup as _backendSetup
    from gpio_pi_backend import check_sensor as _backendCheckSensor
    from gpio_pi_backend import cleanup as _backendCleanup
else:
    from gpio_mock_backend import setup as _backendSetup
    from gpio_mock_backend import check_sensor as _backendCheckSensor
    from gpio_mock_backend import cleanup as _backendCleanup


def setup(trigger_pin, forward_pin, left_pin, right_pin):
    _backendSetup(trigger_pin, forward_pin, left_pin, right_pin)


def checkSensor(trigger_pin, sensor_pin):
    return _backendCheckSensor(trigger_pin, sensor_pin)


def cleanup():
    _backendCleanup()

# Magic numbers and declarations
THRESHOLD_DISTANCE = DEFAULT_THRESHOLD_DISTANCE  # in cm
SensorForwardPin = DEFAULT_SENSOR_FORWARD_PIN
SensorLeftPin = DEFAULT_SENSOR_LEFT_PIN
SensorRightPin = DEFAULT_SENSOR_RIGHT_PIN
TriggerPin = DEFAULT_TRIGGER_PIN


def _readDistance(trigger_pin, sensor_pin, label):
    distance = checkSensor(trigger_pin, sensor_pin)
    if distance == -1:
        logger.warning("%s sensor unavailable", label)
        return None
    return distance


def roam():
    front_distance = _readDistance(TriggerPin, SensorForwardPin, "Front")
    left_distance = _readDistance(TriggerPin, SensorLeftPin, "Left")
    right_distance = _readDistance(TriggerPin, SensorRightPin, "Right")

    if front_distance is not None and front_distance > THRESHOLD_DISTANCE:
        return "Forward"
    elif left_distance is not None and left_distance > THRESHOLD_DISTANCE:
        return "Left"
    elif right_distance is not None and right_distance > THRESHOLD_DISTANCE:
        return "Right"
    else:
        return "Reverse"

def setupRoam():
    logger.info(
        "Roam config: threshold=%scm, trigger=%s, forward=%s, left=%s, right=%s",
        THRESHOLD_DISTANCE,
        TriggerPin,
        SensorForwardPin,
        SensorLeftPin,
        SensorRightPin,
    )
    setup(TriggerPin, SensorForwardPin, SensorLeftPin, SensorRightPin)
    


if __name__ == "__main__":
    configure_logging()
    setupRoam()

    # Ensure trigger is low initially
    time.sleep(0.1)

    logger.info("Reading distance from each sensor once...")

    try:
        front_distance = _readDistance(TriggerPin, SensorForwardPin, "Front")
        left_distance = _readDistance(TriggerPin, SensorLeftPin, "Left")
        right_distance = _readDistance(TriggerPin, SensorRightPin, "Right")

        logger.info(
            "Front distance: %s",
            "unavailable" if front_distance is None else f"{front_distance:.2f} cm",
        )
        logger.info(
            "Left distance: %s",
            "unavailable" if left_distance is None else f"{left_distance:.2f} cm",
        )
        logger.info(
            "Right distance: %s",
            "unavailable" if right_distance is None else f"{right_distance:.2f} cm",
        )

        direction = roam()
        logger.info("Roam decision: %s", direction)
    finally:
        cleanup()
        logger.info("GPIO cleanup complete")
