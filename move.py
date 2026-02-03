def move(direction):
    match direction:
        case "Forward":
            print("Moving forward")
            # Code to move forward
        case "Left":
            print("Turning left")
            # Code to turn left
        case "Right":
            print("Turning right")
            # Code to turn right
        case "Reverse":
            print("Reversing")
            # Code to reverse
        case _:
            print("Unknown direction")
            # Handle unknown direction
    return -1  
        

        
        