import time
import RPi.GPIO as GPIO

#Magic numbers and declarations
THRESHOLD_DISTANCE = 5 # in cm
SensorForwardPin = 17 # Placeholder pin number for forward sensor
SensorLeftPin = 27 # Placeholder pin number for left sensor
SensorRightPin = 22 # Placeholder pin number for right sensor
TriggerPin = 18 # Placeholder pin number for trigger
def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TriggerPin, GPIO.OUT)
    GPIO.setup(SensorForwardPin, GPIO.IN)
    GPIO.setup(SensorLeftPin, GPIO.IN)
    GPIO.setup(SensorRightPin, GPIO.IN)
    

def roam():
    front_distance = checkSensor(SensorForwardPin)
    left_distance = checkSensor(SensorLeftPin)
    right_distance = checkSensor(SensorRightPin)

    if front_distance > THRESHOLD_DISTANCE:
        return "Forward"
    elif left_distance > THRESHOLD_DISTANCE:
        return "Left"
    elif right_distance > THRESHOLD_DISTANCE:
        return "Right"
    else:
        return "Reverse"

def checkSensor(sensorPin):
    # Code to send pulse and measure echo time
    # Send pulse on TriggerPin
    GPIO.output(TriggerPin, True)
    time.sleep(0.00001)  # 10 microsecond pulse
    GPIO.output(TriggerPin, False)

    # Wait for echo to start (go HIGH)
    timeout_start = time.time() + 0.1  # 100ms timeout for echo to start
    while GPIO.input(sensorPin) == 0:
        if time.time() > timeout_start:
            print(f"Sensor {sensorPin}: timeout waiting for echo HIGH")
            return -1  # Timeout - no echo received
    
    pulse_start = time.time()

    # Wait for echo to end (go LOW)
    timeout_end = pulse_start + 0.05  # 50ms max echo duration (covers ~8.5m range)
    while GPIO.input(sensorPin) == 1:
        if time.time() > timeout_end:
            print(f"Sensor {sensorPin}: timeout waiting for echo LOW")
            return -1  # Timeout
    
    pulse_end = time.time()

    # Calculate distance based on time
    duration = pulse_end - pulse_start
    distance = (duration * 34300) / 2  # Speed of sound is 34300 cm/s
    print(f"Sensor {sensorPin}: duration {duration:.6f}s, distance {distance:.2f} cm")
    return distance

if __name__ == "__main__":
    setup()

    # Ensure trigger is low initially
    GPIO.output(TriggerPin, False)
    time.sleep(0.1)

    print("Starting continuous distance measurement (Press Ctrl+C to stop)...")

    try:
        while True:
            # Check forward sensor
            distance = checkSensor(SensorForwardPin)

            if distance == -1:
                print("Forward sensor: Timeout/Error")
            else:
                print(f"Forward distance: {distance:.2f} cm")
            
            time.sleep(0.1)  # Small delay between readings
            
            

    except KeyboardInterrupt:
        print("\nStopping measurements...")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup complete")
