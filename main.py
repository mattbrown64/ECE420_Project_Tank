import os
import sys
import time
import logging

from Camera import CameraObject
from behavior import (
    compute_qr_turn_angle,
    is_target_centered,
    select_highest_priority_target,
    should_activate_trigger_motor,
    should_approach_target,
)
from motor import Motor, MotorMovementControler
from roam import cleanup, roam_angle, setupRoam
from utils import configure_logging, is_raspberry_pi

logger = logging.getLogger(__name__)

LEFT_FORWARD_PIN = int(os.getenv("LEFT_FORWARD_PIN", "10"))
LEFT_REVERSE_PIN = int(os.getenv("LEFT_REVERSE_PIN", "15"))
RIGHT_FORWARD_PIN = int(os.getenv("RIGHT_FORWARD_PIN", "23"))
RIGHT_REVERSE_PIN = int(os.getenv("RIGHT_REVERSE_PIN", "14"))
THIRD_FORWARD_PIN = int(os.getenv("THIRD_FORWARD_PIN", "6"))
THIRD_REVERSE_PIN = os.getenv("THIRD_REVERSE_PIN")
THIRD_REVERSE_PIN = int(THIRD_REVERSE_PIN) if THIRD_REVERSE_PIN is not None else None
CAMERA_TEST_IMAGE = os.getenv("CAMERA_TEST_IMAGE")
DRIVE_DURATION_MS = int(os.getenv("DRIVE_DURATION_MS", "500"))
CENTERED_DRIVE_DURATION_MS = int(os.getenv("CENTERED_DRIVE_DURATION_MS", str(DRIVE_DURATION_MS)))


def initialize_motors() -> MotorMovementControler:
    left_motor = Motor("Left", LEFT_FORWARD_PIN, LEFT_REVERSE_PIN)
    right_motor = Motor("Right", RIGHT_FORWARD_PIN, RIGHT_REVERSE_PIN)
    trigger_motor = Motor("Trigger", THIRD_FORWARD_PIN, THIRD_REVERSE_PIN)

    left_motor.connect()
    right_motor.connect()
    trigger_motor.connect()

    return MotorMovementControler(left_motor, right_motor, trigger_motor)


def main():
    wait_time = 2  # Time to wait between movement cycles
    logger.info("Starting tank control loop")
    setupRoam()  # Initialize GPIO pins for roaming sensors

    motor_controller = initialize_motors()

    camera = None
    try:
        camera = CameraObject(image_path=CAMERA_TEST_IMAGE) if CAMERA_TEST_IMAGE else CameraObject()
    except Exception as e:
        logger.warning("Camera initialization failed; continuing with roam-only fallback: %s", e)
        camera = None

    try:
        while True:
            detections = []
            if camera is not None:
                try:
                    detections = camera.read_qr(save_path='capture.jpg')
                except Exception as exc:
                    logger.warning("Camera read failed; using roam fallback: %s", exc)
                    detections = []

            target = select_highest_priority_target(detections)
            if target is not None:
                logger.info("QR target detected: %s", target)
                target_label = target.get('label') or target.get('text') or target.get('raw')
                print(f"Highest priority target: {target_label}")

            trigger_active = should_activate_trigger_motor(target)
            if trigger_active:
                logger.info("Trigger motor enabled for enemy in center third.")

            if target is not None:
                angle = compute_qr_turn_angle(target)
                if should_approach_target(target):
                    logger.info("QR target is close enough to approach")
                    if motor_controller.drive(DRIVE_DURATION_MS / 1000.0, trigger=trigger_active) != 0:
                        logger.error("Drive failed when approaching target")
                        return 1
                elif is_target_centered(target):
                    logger.info("QR target is roughly centered; driving forward a short distance")
                    if motor_controller.drive(CENTERED_DRIVE_DURATION_MS / 1000.0, trigger=trigger_active) != 0:
                        logger.error("Drive failed while moving forward on centered QR target")
                        return 1
                else:
                    logger.info("Turning %.1f degrees to center QR target", angle)
                    if motor_controller.turn(angle, trigger=trigger_active) != 0:
                        logger.error("Turn failed for QR target angle: %s", angle)
                        return 1
            else:
                angle = roam_angle()
                logger.info("Roam angle: %.1f", angle)
                if angle == 0.0:
                    if motor_controller.drive(DRIVE_DURATION_MS / 1000.0) != 0:
                        logger.error("Drive failed during roam forward")
                        return 1
                else:
                    if motor_controller.turn(angle) != 0:
                        logger.error("Turn failed during roam: %s", angle)
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
