def move(direction):
    match direction:
        case "Forward":
            print("Moving forward")
            return 0
            # Code to move forward
        case "Left":
            print("Turning left")
            return 0
            # Code to turn left
        case "Right":
            print("Turning right")
            return 0
            # Code to turn right
        case "Reverse":
            print("Reversing")
            return 0
            # Code to reverse
        case _:
            print("Unknown direction")
            # Handle unknown direction
    return -1  
        

        
        