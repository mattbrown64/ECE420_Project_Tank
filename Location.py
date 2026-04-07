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
        # Extract coordinates
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


def qr_info_from_frame(frame):
    """Detect QR codes with both data and location in an OpenCV frame (BGR)."""
    if frame is None or frame.size == 0:
        return []

    decoded = pyzbar.decode(frame)
    qr_info = []
    for barcode in decoded:
        if barcode.type != 'QRCODE':
            continue
        data = barcode.data.decode('utf-8', errors='replace')
        rect = barcode.rect
        # Extract coordinates
        x1, y1 = rect.left, rect.top
        x2, y2 = rect.left + rect.width, rect.top + rect.height
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        qr_info.append({
            'data': data,
            'location': {
                'top_left': (x1, y1),
                'bottom_right': (x2, y2),
                'center': (center_x, center_y),
                'width': rect.width,
                'height': rect.height
            }
        })

    return qr_info

if __name__ == '__main__':
    camera = None
    try:
        camera = CameraObject()
        frame = camera.read_frame(save_path='capture.jpg')
        qr_info = qr_info_from_frame(frame)
        print('Captured image and ran QR info detection.')

        if qr_info:
            for qr in qr_info:
                print(f"Detected: {qr['data']} at center {qr['location']['center']}")
        else:
            print('No QR code detected in image.')
    except Exception as e:
        print('Camera operation failed:', e)
    finally:
        if camera is not None:
            camera.close()
