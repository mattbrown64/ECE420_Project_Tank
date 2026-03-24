import subprocess
import os

print("Taking a photo using native Pi tools...")

result = subprocess.run(["rpicam-still", "-o", "python_test.jpg"], capture_output=True, text=True)

if result.returncode == 0:
    print("Success! 'python_test.jpg' has been created.")
else:
    print("Error: The camera didn't fire.")
    print("Error details:", result.stderr)