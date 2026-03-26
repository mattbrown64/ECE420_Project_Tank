from roam import roam, setupRoam, cleanup
from move import move
import time
import sys
#import RPi.GPIO as GPIO
import logging
from utils import configure_logging, is_raspberry_pi
from Camera import CameraObject

logger = logging.getLogger(__name__)
left_pin = 0  # GPIO pin for left motor control
right_pin = 0  # GPIO pin for right motor control

def main():
    wait_time = 2  # Time to wait between movements
    logger.info("Starting tank control loop")
    setupRoam()  # Initialize GPIO pins for roaming sensors
    # Initialize motors here if needed, e.g. motor_Left = Motor(left_pin), motor_Right = Motor(right_pin)
    motor_Left = Motor("Left", left_pin)  # Placeholder for motor initialization
    motor_Right = Motor("Right", right_pin)  # Placeholder for motor initialization

    camera = None
    try:
        camera = CameraObject()
    except Exception as e:
        logger.exception("Could not initialize camera")
        return 1

    try:
        while True:
            try:
                detections = camera.read_qr(save_path='capture.jpg')
            except Exception as e:
                logger.exception("Camera read failed")
                detections = []

            logger.debug("Camera detections: %s", detections)
            if detections:
                print("Target Detected:", detections)
                # Add your target-handling logic here.
            else:
                direction = roam()
                logger.debug("Roam decision: %s", direction)
                match direction:
                    case "Forward":
                        if move("Forward", motor_Left, motor_Right) == -1:
                            logger.error("Movement failed for direction: Forward")
                            return 1
                    case "Left":
                        if move("Left", motor_Left, motor_Right) == -1:
                            logger.error("Movement failed for direction: Left")
                            return 1
                    case "Right":
                        if move("Right", motor_Left, motor_Right) == -1:
                            logger.error("Movement failed for direction: Right")
                            return 1
                    case "Reverse":
                        if move("Reverse", motor_Left, motor_Right) == -1:
                            logger.error("Movement failed for direction: Reverse")
                            return 1
                    case _:
                        logger.warning("Unknown roam decision: %s", direction)
                        return 1

            time.sleep(wait_time)
    finally:
        if camera is not None:
            camera.close()


if __name__ == "__main__":
    configure_logging()
    if not is_raspberry_pi():
        logger.warning("Running outside Raspberry Pi hardware")

    exit_code = 0
    try:
        exit_code = main()
    except KeyboardInterrupt:
        logger.info("Stopping measurements...")
    except Exception:
        logger.exception("Fatal runtime error")
        exit_code = 1
    finally:
        cleanup()
        logger.info("GPIO cleanup complete")
    sys.exit(exit_code)
