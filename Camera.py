import cv2
import numpy as np
from picamera2 import Picamera2
from pyzbar import pyzbar
import time


def Capture(file_path='capture.jpg'):
    """Capture one image frame from Raspberry Pi camera using picamera2.

    Overwrites existing file. Raises RuntimeError on any failure.
    """

    try:
        picam = Picamera2()
    except Exception as e:
        raise RuntimeError(f'Failed to initialize Picamera2: {e}')

    try:
        config = picam.create_still_configuration(main={'size': (1280, 720)})
        picam.configure(config)
        picam.start()

        # Allow auto exposure/white balance to stabilize
        time.sleep(0.5)

        frame = picam.capture_array()
    except Exception as e:
        raise RuntimeError(f'Failed to capture frame from Picamera2: {e}')
    finally:
        try:
            picam.stop()
        except Exception:
            pass
        try:
            picam.close()
        except Exception:
            pass

    if frame is None or frame.size == 0:
        raise RuntimeError('Failed to capture valid frame from Picamera2')

    # picamera2 returns RGB, OpenCV writes BGR.
    try:
        bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    except Exception as e:
        raise RuntimeError(f'Failed to convert captured frame to BGR: {e}')

    ok = cv2.imwrite(file_path, bgr)
    if not ok:
        raise RuntimeError(f'Failed to write image to "{file_path}"')

    return file_path


def Detect(file_path='capture.jpg'):
    """Detect QR codes in an image file.

    Returns a list of decoded QR data strings. If no QR codes are found, returns an empty list.
    Raises FileNotFoundError if the image cannot be loaded.
    """
    img = cv2.imread(file_path)
    if img is None:
        raise FileNotFoundError(f'Cannot load image from "{file_path}"')

    decoded = pyzbar.decode(img)
    qr_strings = []
    for barcode in decoded:
        if barcode.type != 'QRCODE':
            continue
        qr_strings.append(barcode.data.decode('utf-8', errors='replace'))

    return qr_strings


def Camera(file_path='capture.jpg'):
    """Capture an image and detect QR codes in it.

    Returns the same list of detection dicts as Detect().
    """
    Capture(file_path)
    return Detect(file_path)


if __name__ == '__main__':
    try:
        detections = Camera('capture.jpg')
        print('Captured image and ran QR detection.')

        if detections:
            print(f'QR code detected: {detections}')
        else:
            print('No QR code detected in image.')
    except Exception as e:
        print('Camera operation failed:', e)

