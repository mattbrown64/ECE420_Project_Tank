
import importlib
import logging
import os
import time

logger = logging.getLogger(__name__)
_PWM_FREQUENCY_HZ = 100  # PWM frequency for motor speed control


def _import_rpi_gpio():
    try:
        return importlib.import_module("RPi.GPIO")
    except ModuleNotFoundError:
        return None


class Motor:
    def __init__(self, name, ForwardPin, ReversePin=None, inverted=False):
        self.name = name
        self.forward_pin = ForwardPin
        self.reverse_pin = ReversePin
        self.inverted = inverted
        self._gpio = _import_rpi_gpio()
        self._pwm_forward = None
        self._pwm_reverse = None
        self._connected = False
        self._last_duty_value = 0.0

    def connect(self):
        if self._connected:
            return 0

        if self._gpio is None:
            from gpio_mock_backend import setup_motor_pwm
            self._pwm_forward = setup_motor_pwm(self.forward_pin, _PWM_FREQUENCY_HZ)
            if self.reverse_pin is not None:
                self._pwm_reverse = setup_motor_pwm(self.reverse_pin, _PWM_FREQUENCY_HZ)
        else:
            self._gpio.setwarnings(False)
            if self._gpio.getmode() is None:
                self._gpio.setmode(self._gpio.BCM)
            self._gpio.setup(self.forward_pin, self._gpio.OUT)
            self._pwm_forward = self._gpio.PWM(self.forward_pin, _PWM_FREQUENCY_HZ)
            if self.reverse_pin is not None:
                self._gpio.setup(self.reverse_pin, self._gpio.OUT)
                self._pwm_reverse = self._gpio.PWM(self.reverse_pin, _PWM_FREQUENCY_HZ)

        self._pwm_forward.start(0)
        if self._pwm_reverse is not None:
            self._pwm_reverse.start(0)
        self._connected = True
        logger.info(
            "Motor %s connected on forward_pin=%s reverse_pin=%s",
            self.name,
            self.forward_pin,
            self.reverse_pin,
        )
        return 0

    def disconnect(self):
        if not self._connected:
            return 0

        if self._pwm_forward is not None:
            try:
                self._pwm_forward.ChangeDutyCycle(0)
                self._pwm_forward.stop()
            except Exception:
                logger.exception("Error stopping forward PWM for motor %s", self.name)

        if self._pwm_reverse is not None:
            try:
                self._pwm_reverse.ChangeDutyCycle(0)
                self._pwm_reverse.stop()
            except Exception:
                logger.exception("Error stopping reverse PWM for motor %s", self.name)

        self._pwm_forward = None
        self._pwm_reverse = None
        self._connected = False
        logger.info("Motor %s disconnected", self.name)
        return 0

    def Move(self, Duty_Cycle=0.0):
        """Move motor with duty cycle from -1.0 to 1.0.

        Positive values drive the forward pin, negative values drive the reverse pin.
        """
        if self._pwm_forward is None:
            if self.connect() != 0:
                logger.error("Motor %s failed to connect", self.name)
                return -1

        try:
            duty_value = float(Duty_Cycle)
        except (TypeError, ValueError):
            logger.error("Motor %s Move received invalid Duty_Cycle: %s", self.name, Duty_Cycle)
            return -1

        duty_value = max(-1.0, min(1.0, duty_value))
        if self.inverted:
            duty_value = -duty_value
        pwm_value = abs(duty_value) * 100.0

        if self._last_duty_value * duty_value < 0:
            # Brake before switching direction to prevent the driver from locking up.
            self._pwm_forward.ChangeDutyCycle(0)  # pyright: ignore[reportOptionalMemberAccess]
            if self._pwm_reverse is not None:
                self._pwm_reverse.ChangeDutyCycle(0)  # pyright: ignore[reportOptionalMemberAccess]
            time.sleep(0.01)

        if duty_value > 0:
            self._pwm_forward.ChangeDutyCycle(pwm_value)  # pyright: ignore[reportOptionalMemberAccess]
            if self._pwm_reverse is not None:
                self._pwm_reverse.ChangeDutyCycle(0) # pyright: ignore[reportOptionalMemberAccess]
        elif duty_value < 0:
            if self._pwm_reverse is None:
                logger.warning("Motor %s has no reverse pin configured; stopping instead of reversing", self.name)
                self._pwm_forward.ChangeDutyCycle(0) # pyright: ignore[reportOptionalMemberAccess]
            else:
                self._pwm_forward.ChangeDutyCycle(0) # pyright: ignore[reportOptionalMemberAccess]
                self._pwm_reverse.ChangeDutyCycle(pwm_value) # pyright: ignore[reportOptionalMemberAccess]
        else:
            self._pwm_forward.ChangeDutyCycle(0) # pyright: ignore[reportOptionalMemberAccess]
            if self._pwm_reverse is not None:
                self._pwm_reverse.ChangeDutyCycle(0) # pyright: ignore[reportOptionalMemberAccess]

        self._last_duty_value = duty_value

        logger.debug(
            "Motor %s set duty_cycle=%s -> forward=%s reverse=%s",
            self.name,
            duty_value,
            pwm_value if duty_value >= 0 else 0,
            pwm_value if duty_value <= 0 else 0,
        )
        return 0

TURN_360_MS = int(os.getenv("TURN_360_MS", "2000"))
DRIVE_SPEED = float(os.getenv("DRIVE_SPEED", "1.0"))
TURN_SPEED = float(os.getenv("TURN_SPEED", "1.0"))


class MotorMovementControler:
    def __init__(self, motor_Left: Motor, motor_Right: Motor, trigger_motor: Motor | None = None):
        self.motor_Left = motor_Left
        self.motor_Right = motor_Right
        self.trigger_motor = trigger_motor
        self._trigger_active = False

    def _set_turn_motion(self, angle_deg: float) -> int:
        if angle_deg == 0.0:
            return 0

        if angle_deg > 0:
            logger.info("Turning right %.1f degrees", angle_deg)
            self.motor_Left.Move(TURN_SPEED)
            self.motor_Right.Move(-TURN_SPEED)
        else:
            logger.info("Turning left %.1f degrees", angle_deg)
            self.motor_Left.Move(-TURN_SPEED)
            self.motor_Right.Move(TURN_SPEED)
        return 0

    def _set_drive_motion(self, speed: float) -> int:
        logger.info("Driving forward at speed %s", speed)
        self.motor_Left.Move(speed)
        self.motor_Right.Move(speed)
        return 0

    def _set_trigger_motor(self, enabled: bool) -> int:
        if self.trigger_motor is None:
            return 0

        if enabled:
            if not self._trigger_active:
                logger.info("Starting trigger motor")
                self.trigger_motor.Move(1.0)
                self._trigger_active = True
        else:
            if self._trigger_active:
                logger.info("Stopping trigger motor")
                self.trigger_motor.Move(0.0)
                self._trigger_active = False
        return 0

    def turn(self, angle_deg: float, trigger: bool = False) -> int:
        if self._set_turn_motion(angle_deg) != 0:
            return -1

        self._set_trigger_motor(trigger)
        duration = abs(angle_deg) / 360.0 * TURN_360_MS / 1000.0
        time.sleep(max(0.0, duration))
        self.stop()
        return 0

    def drive(self, duration_s: float, speed: float = DRIVE_SPEED, trigger: bool = False) -> int:
        if self._set_drive_motion(speed) != 0:
            return -1

        self._set_trigger_motor(trigger)
        time.sleep(max(0.0, duration_s))
        self.stop()
        return 0

    def stop(self) -> int:
        logger.info("Stopping motors")
        self.motor_Left.Move(0.0)
        self.motor_Right.Move(0.0)
        self._set_trigger_motor(False)
        return 0

    def manual_control(self, left_speed, right_speed):
        logger.info("Manual control: left_speed=%s right_speed=%s", left_speed, right_speed)
        self.motor_Left.Move(left_speed)
        self.motor_Right.Move(right_speed)
        return 0



if __name__ == "__main__":
    import time

    try:
        import pygame  # type: ignore[import]
    except ImportError:
        print("pygame is required for controller input. Install it with 'pip install pygame'.")
        raise

    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No joystick found. Please connect a controller and restart.")
        pygame.quit()
        raise SystemExit(1)

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Using joystick: {joystick.get_name()}")
    print("Left stick vertical = left motor, right stick vertical = right motor, axis 5 vertical = third motor")
    print("Button 0 or CTRL+C to quit")
    
    left_forward_pin = 10
    left_reverse_pin = 15
    right_forward_pin = 23 #Flipped
    right_reverse_pin = 14 #Flipped
    third_forward_pin = 6
    third_reverse_pin = None

    left_motor = Motor("Left", left_forward_pin, left_reverse_pin)
    right_motor = Motor("Right", right_forward_pin, right_reverse_pin)
    third_motor = Motor("Third", third_forward_pin, third_reverse_pin)
    controller = MotorMovementControler(left_motor, right_motor)

    try:
        left_motor.connect()
        right_motor.connect()
        third_motor.connect()

        last_left = None
        last_right = None
        last_third = None

        while True:
            pygame.event.pump()
            if joystick.get_numaxes() < 2:
                print("Joystick does not have enough axes for left and right stick input.")
                break
            if joystick.get_numaxes() <= 5:
                print("Joystick does not have axis 5 for the third motor.")
                break

            left_axis = joystick.get_axis(1)
            right_axis = joystick.get_axis(4 if joystick.get_numaxes() > 4 else 3 if joystick.get_numaxes() > 3 else 2)
            third_axis = joystick.get_axis(5)
            left_speed = max(-1.0, min(1.0, round(-left_axis, 1)))
            right_speed = max(-1.0, min(1.0, round(-right_axis, 1)))
            third_speed = max(0.0, min(1.0, round((third_axis + 1) / 2, 2)))

            if last_left is None or last_right is None or last_third is None:
                should_update = True
            else:
                should_update = (
                    abs(left_speed - last_left) >= 0.05 or
                    abs(right_speed - last_right) >= 0.05 or
                    abs(third_speed - last_third) >= 0.05
                )

            if should_update:
                controller.manual_control(left_speed, right_speed)
                third_motor.Move(third_speed)
                print(
                    f"left_speed={left_speed:.1g} right_speed={right_speed:.1g} third_speed={third_speed:.1g}"
                )
                last_left = left_speed
                last_right = right_speed
                last_third = third_speed

            time.sleep(0.05)
    except KeyboardInterrupt:
        print("Exiting controller input loop")
    finally:
        left_motor.disconnect()
        right_motor.disconnect()
        third_motor.disconnect()
        pygame.quit()
   