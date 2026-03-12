import cv2
from pyzbar.pyzbar import decode

cap = cv2.VideoCapture(0)

print("Scanning for QR codes... Press 'q' to quit.")

while True:
    success, frame = cap.read()
    if not success:
        break


    for code in decode(frame):

        data = code.data.decode('utf-8')
        

        if data == 'Friend!':
            print("Welcome, buddy! 🤝")
        elif data == 'Enemy!':
            print("Intruder alert! 🛡️")
        elif data == 'BiggerEnemy!':
            print("RUN! It's a boss fight! 🐉")
        elif data == 'Lover!':
            print("Heart eyes only. 😍")
        else:
            print(f"Unknown code detected: {data}")

    cv2.imshow('PiScan', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()