import time
#Magic numbers and declarations
THRESHOLD_DISTANCE = 20  # in cm
SensorForwardPin = 1 # Placeholder pin number for forward sensor
SensorLeftPin = 2 # Placeholder pin number for left sensor
SensorRightPin = 3 # Placeholder pin number for right sensor
TriggerPin = 4 # Placeholder pin number for trigger
    

def roam():
    

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

def checkSensor(sensorPin):
    # Code to send pulse and measure echo time
    #Send pulse on TriggerPin
    Start=time.time()
    #Wait for echo on sensorPin
    End=time.time()
    #Calculate distance based on time
    duration = End - Start
    distance = (duration * 34300) / 2  # Speed of sound is 34300 cm/s
    return distance