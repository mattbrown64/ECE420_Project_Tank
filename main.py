from roam import roam
from move import move
import time

def main():
    target_found = False  # Initialize camera
    wait_time = 0.1  # Time to wait between movements
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
    main()
