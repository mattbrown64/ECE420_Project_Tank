from roam import roam, setupRoam, cleanup
from move import move
import time
import sys
#import RPi.GPIO as GPIO
import logging
from utils import configure_logging, is_raspberry_pi
from Camera import CameraObject
from Emotions import show_smiley, show_angry, show_heart_eyes
from Music import play_background_music, stop_background_music

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
                # Map QR payload to emotion display.
                normalized = [code.strip().lower() for code in detections]
                if any(code in ("enemy!", "biggerenemy!") for code in normalized):
                    show_angry()
                    if "biggerenemy!" in normalized:
                        play_background_music("bigger_enemy")
                    else:
                        play_background_music("enemy")
                elif "lover!" in normalized:
                    show_heart_eyes()
                    play_background_music("lover")
                elif "friend!" in normalized:
                    show_smiley()
                    play_background_music("friend")
                else:
                    # Fallback if detection text is unknown.
                    show_smiley()
                    stop_background_music()
            else:
                play_background_music("friend")
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
        stop_background_music()


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
