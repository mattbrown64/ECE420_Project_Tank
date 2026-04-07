import cv2
import numpy as np
from picamera2 import Picamera2
from pyzbar import pyzbar
import time
from Location import qr_location_from_frame


def detect_qr_info_from_frame(frame):
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


class CameraObject:
    def __init__(self, size=(1280, 720), warmup=0.5):
        self.picam = None
        self.size = size
        self.warmup = warmup

        try:
            self.picam = Picamera2()
            config = self.picam.create_still_configuration(main={'size': self.size})
            self.picam.configure(config)
            self.picam.start()
            time.sleep(self.warmup)
        except Exception as e:
            self.close()
            raise RuntimeError(f'Failed to initialize Camera: {e}')

    def read_frame(self, save_path=None):
        if self.picam is None:
            raise RuntimeError('Camera is not initialized')

        frame = self.picam.capture_array()
        if frame is None or frame.size == 0:
            raise RuntimeError('Failed to capture frame from camera')

        try:
            bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        except Exception as e:
            raise RuntimeError(f'Failed to convert frame to BGR: {e}')

        if save_path:
            ok = cv2.imwrite(save_path, bgr)
            if not ok:
                raise RuntimeError(f'Failed to write image to "{save_path}"')

        return bgr

    def read_qr(self, save_path=None):
        frame = self.read_frame(save_path=save_path)
        return detect_qr_from_frame(frame)

    def close(self):
        if self.picam is not None:
            try:
                self.picam.stop()
            except Exception:
                pass
            try:
                self.picam.close()
            except Exception:
                pass
            self.picam = None


def Capture(file_path='capture.jpg'):
    camera = CameraObject()
    try:
        frame = camera.read_frame(save_path=file_path)
    finally:
        camera.close()

    return file_path


def Detect(file_path='capture.jpg'):
    img = cv2.imread(file_path)
    if img is None:
        raise FileNotFoundError(f'Cannot load image from "{file_path}"')

    return detect_qr_from_frame(img)


if __name__ == '__main__':
    camera = None
    try:
        camera = CameraObject()
        location = qr_location_from_frame()
        detections = camera.read_qr(save_path='capture.jpg')
        print('Captured image and ran QR detection.')

        if detections:
            print(f'QR code detected: {detections}')
        if location:
            for qr in location:
                print(f"QR code location: {qr}")
        else:
            print('No QR code detected in image.')
    except Exception as e:
        print('Camera operation failed:', e)
    finally:
        if camera is not None:
            camera.close()

