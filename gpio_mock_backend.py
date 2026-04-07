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


class MockPWM:
    def __init__(self, pin, frequency):
        self.pin = pin
        self.frequency = frequency
        self.duty_cycle = 0.0
        logger.info("MockPWM initialized on pin %s at %s Hz", pin, frequency)

    def start(self, duty_cycle):
        self.duty_cycle = duty_cycle
        logger.info("MockPWM pin %s started at duty cycle %.1f%%", self.pin, duty_cycle)

    def ChangeDutyCycle(self, duty_cycle):
        self.duty_cycle = duty_cycle
        logger.info("MockPWM pin %s duty cycle changed to %.1f%%", self.pin, duty_cycle)

    def stop(self):
        logger.info("MockPWM pin %s stopped", self.pin)
        self.duty_cycle = 0.0


def setup_motor_pwm(pin, frequency=100):
    logger.info("Mock GPIO setup motor PWM pin %s at %s Hz", pin, frequency)
    return MockPWM(pin, frequency)


def cleanup():
    logger.info("Mock GPIO cleanup complete")
