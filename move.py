import logging

logger = logging.getLogger(__name__)


def move(direction):
    match direction:
        case "Forward":
            logger.info("Moving forward")
            return 0
            # Code to move forward
        case "Left":
            logger.info("Turning left")
            return 0
            # Code to turn left
        case "Right":
            logger.info("Turning right")
            return 0
            # Code to turn right
        case "Reverse":
            logger.info("Reversing")
            return 0
            # Code to reverse
        case _:
            logger.warning("Unknown direction: %s", direction)
            # Handle unknown direction
    return -1  
        

        
        