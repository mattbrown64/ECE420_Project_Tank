from roam import roam, setupRoam, cleanup
from move import move
import time
import sys
#import RPi.GPIO as GPIO
import logging
from utils import configure_logging, is_raspberry_pi

logger = logging.getLogger(__name__)

def main():
    target_found = False  # Initialize camera
    wait_time = 2  # Time to wait between movements
    logger.info("Starting tank control loop")
    setupRoam()  # Initialize GPIO pins for roaming sensors
    while True:
        # Check camera for target
        if target_found:
            pass  # Process camera input if available
        else:
            direction = roam()
            logger.debug("Roam decision: %s", direction)
            match direction:
                case "Forward":
                    if move("Forward") == -1:
                        logger.error("Movement failed for direction: Forward")
                        return 1
                case "Left":
                    if move("Left") == -1:
                        logger.error("Movement failed for direction: Left")
                        return 1
                case "Right":
                    if move("Right") == -1:
                        logger.error("Movement failed for direction: Right")
                        return 1
                case "Reverse":
                    if move("Reverse") == -1:
                        logger.error("Movement failed for direction: Reverse")
                        return 1
                case _:
                    logger.warning("Unknown roam decision: %s", direction)
                    return 1
            pass  # Placeholder for movement code
        time.sleep(wait_time)

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
