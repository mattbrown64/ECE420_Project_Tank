import time

def roam():
    #Magic numbers and declarations
    THRESHOLD_DISTANCE = 20  # in cm
    

    #send pulse to sonar
    #record pol time for each echo

    #Find front distance
    front_distance = 30 #Placeholder value
    #Find Left distance
    left_distance = 20 #Placeholder value
    #Find Right distance
    right_distance = 10 #Placeholder value

    if front_distance > THRESHOLD_DISTANCE:
        return "Forward"
    elif left_distance > THRESHOLD_DISTANCE:
        return "Left"
    elif right_distance > THRESHOLD_DISTANCE:
        return "Right"
    else:
        return "Reverse"

    pass