import cv2
import numpy as np
from picamera2 import Picamera2
from pyzbar import pyzbar
import time
from Camera import CameraObject

def qr_location_from_frame(frame):
    if frame is None or frame.size == 0:
        return []

    decoded = pyzbar.decode(frame)
    qr_locations = []
    for barcode in decoded:
        if barcode.type != 'QRCODE':
            continue
        rect = barcode.rect
        x1, y1 = rect.left, rect.top
        x2, y2 = rect.left + rect.width, rect.top + rect.height
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        qr_locations.append({
            'top_left': (x1, y1),
            'bottom_right': (x2, y2),
            'center': (center_x, center_y),
            'width': rect.width,
            'height': rect.height
        })

    return qr_locations


if __name__ == '__main__':
    try:
        img = cv2.imread('capture.jpg')
        if img is None:
            print('Failed to load qrcodeinspace.jpg')
        else:
            qr_locations = qr_location_from_frame(img)
            print('Captured image and ran QR location detection.')

            if qr_locations:
                for qr in qr_locations:
                    print(f"QR code location: {qr}")
            else:
                print('No QR code detected in image.')
    except Exception as e:
        print('Operation failed:', e)
