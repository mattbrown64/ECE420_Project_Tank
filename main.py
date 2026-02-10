from roam import roam, setup
from move import move
import time
import RPi.GPIO as GPIO

def main():
    target_found = False  # Initialize camera
    wait_time = 2  # Time to wait between movements
    setup()  # Initialize GPIO pins for roaming sensors
    while True:
        # Check camera for target
        if target_found:
            pass  # Process camera input if available
        else:
            direction = roam()
            match direction:
                case "Forward":
                    if move("Forward") == -1:
                        break  # Exit if move fails
                case "Left":
                    if move("Left") == -1:
                        break  # Exit if move fails
                case "Right":
                    if move("Right") == -1:
                        break  # Exit if move fails
                case "Reverse":
                    if move("Reverse") == -1:
                        break  # Exit if move fails
                case _:
                    break
            pass  # Placeholder for movement code
        time.sleep(wait_time)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopping measurements...")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup complete")
