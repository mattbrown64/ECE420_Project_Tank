import os
import cv2
import numpy as np
from pyzbar import pyzbar
import time

try:
    from picamera2 import Picamera2
except ImportError:
    Picamera2 = None


def detect_qr_from_frame(frame):
    if frame is None or frame.size == 0:
        return []

    frame_height, frame_width = frame.shape[:2]
    decoded = pyzbar.decode(frame)
    detections = []
    for barcode in decoded:
        if barcode.type != 'QRCODE':
            continue

        text = barcode.data.decode('utf-8', errors='replace')
        rect = getattr(barcode, 'rect', None)
        polygon = getattr(barcode, 'polygon', None)

        if rect is not None:
            rect_data = {
                'left': getattr(rect, 'left', getattr(rect, 'x', 0)),
                'top': getattr(rect, 'top', getattr(rect, 'y', 0)),
                'width': getattr(rect, 'width', 0),
                'height': getattr(rect, 'height', 0),
            }
            center_x = rect_data['left'] + rect_data['width'] / 2
            center_y = rect_data['top'] + rect_data['height'] / 2
            area = rect_data['width'] * rect_data['height']
        else:
            rect_data = None
            center_x = None
            center_y = None
            area = None

        if polygon is not None:
            polygon_points = [(p.x, p.y) for p in polygon]
        else:
            polygon_points = []

        detections.append({
            'text': text,
            'raw': text,
            'rect': rect_data,
            'polygon': polygon_points,
            'center': {'x': center_x, 'y': center_y} if center_x is not None else None,
            'frame_width': frame_width,
            'frame_height': frame_height,
            'area': area,
            'area_ratio': area / (frame_width * frame_height) if area is not None and frame_width * frame_height > 0 else None,
        })

    return detections


class CameraObject:
    def __init__(self, size=(1280, 720), warmup=0.5, image_path=None):
        self.picam = None
        self.size = size
        self.warmup = warmup
        self.image_path = image_path

        if self.image_path is not None:
            if not os.path.isfile(self.image_path):
                raise FileNotFoundError(f'Camera image file not found: {self.image_path}')
            return

        if Picamera2 is None:
            raise RuntimeError(
                'Picamera2 is unavailable in this environment. Use a test image via image_path or run on Raspberry Pi with camera support.'
            )

        try:
            camera_info = Picamera2.global_camera_info()
            if not camera_info:
                raise RuntimeError(
                    'No cameras found. Ensure the Raspberry Pi camera is connected, enabled, and libcamera is configured correctly.'
                )

            last_exc = None
            for info in camera_info:
                camera_num = info.get('Num', 0)
                try:
                    self.picam = Picamera2(camera_num=camera_num)
                    break
                except Exception as exc:
                    last_exc = exc

            if self.picam is None:
                raise last_exc or RuntimeError('Failed to initialize any Picamera2 camera')

            config = self.picam.create_still_configuration(main={'size': self.size})
            self.picam.configure(config)
            self.picam.start()
            time.sleep(self.warmup)
        except Exception as e:
            self.close()
            raise RuntimeError(f'Failed to initialize Camera: {e}')

    def read_frame(self, save_path=None):
        if self.image_path is not None:
            bgr = cv2.imread(self.image_path)
            if bgr is None or bgr.size == 0:
                raise RuntimeError(f'Failed to load image from {self.image_path}')
            if save_path:
                ok = cv2.imwrite(save_path, bgr)
                if not ok:
                    raise RuntimeError(f'Failed to write image to "{save_path}"')
            return bgr

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
        camera.read_frame(save_path=file_path)
    finally:
        camera.close()

    return file_path


def Detect(file_path='capture.jpg'):
    img = cv2.imread(file_path)
    if img is None:
        raise FileNotFoundError(f'Cannot load image from "{file_path}"')

    return detect_qr_from_frame(img)


def read_qr_from_file(image_path, save_path=None):
    camera = CameraObject(image_path=image_path)
    try:
        return camera.read_qr(save_path=save_path)
    finally:
        camera.close()


if __name__ == '__main__':
    camera = None
    try:
        camera = CameraObject()
        detections = camera.read_qr(save_path='capture.jpg')
        print('Captured image and ran QR detection.')

        if detections:
            print(f'QR code detected: {detections}')
        else:
            print('No QR code detected in image.')
    except Exception as e:
        print('Camera operation failed:', e)
    finally:
        if camera is not None:
            camera.close()

