import logging


logger = logging.getLogger(__name__)



def move(direction,motor_Left,motor_Right):
    match direction:
        case "Forward":
            logger.info("Moving forward")
            motor_Left.Move(1.0)
            motor_Right.Move(1.0)
            return 0
            # Code to move forward
        case "Left":
            logger.info("Turning left")
            motor_Left.Move(0.0)
            motor_Right.Move(1.0)
            return 0
            # Code to turn left
        case "Right":
            logger.info("Turning right")
            motor_Left.Move(1.0)
            motor_Right.Move(0.0)
            return 0
            # Code to turn right
        case "Reverse":
            logger.info("Reversing")
            motor_Left.Move(-1.0)
            motor_Right.Move(-1.0)
            return 0
            # Code to reverse
        case _:
            logger.warning("Unknown direction: %s", direction)
            # Handle unknown direction
    return -1  
        

        
        