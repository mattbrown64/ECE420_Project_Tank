import os
from typing import Any, Iterable, Optional

from QRCodes import PRIORITY_QR_CODES, normalize_qr_label

QR_APPROACH_AREA_RATIO = float(os.getenv("QR_APPROACH_AREA_RATIO", "0.08"))
MAX_QR_TURN_DEGREE = float(os.getenv("MAX_QR_TURN_DEGREE", "90.0"))
QR_CENTER_DEADZONE_DEG = float(os.getenv("QR_CENTER_DEADZONE_DEG", "5.0"))


def _normalize_detection_payload(detection: Any) -> Optional[str]:
    if isinstance(detection, str):
        return normalize_qr_label(detection)

    if isinstance(detection, dict):
        raw_text = detection.get('text') or detection.get('raw')
        return normalize_qr_label(raw_text)

    return None


def select_highest_priority_target(detections: Iterable[Any]) -> Optional[dict]:
    """Return the highest-priority QR detection from an iterable of decoded payloads."""
    labeled_detections = []
    for detection in detections:
        label = _normalize_detection_payload(detection)
        if label is not None:
            labeled_detections.append((label, detection))

    for target in PRIORITY_QR_CODES:
        for label, detection in labeled_detections:
            if label == target:
                return {**detection, 'label': target}

    return None


def compute_qr_turn_angle(target: Optional[dict]) -> float:
    """Compute the approximate turn angle needed to center a QR target."""
    if target is None:
        return 0.0

    center = target.get('center') or {}
    frame_width = target.get('frame_width')
    x = center.get('x') if isinstance(center, dict) else None

    if x is None or frame_width is None or frame_width <= 0:
        return 0.0

    offset = (x - frame_width / 2.0) / (frame_width / 2.0)
    angle = max(-MAX_QR_TURN_DEGREE, min(MAX_QR_TURN_DEGREE, offset * MAX_QR_TURN_DEGREE))
    if abs(angle) < QR_CENTER_DEADZONE_DEG:
        return 0.0
    return angle


def is_target_centered(target: Optional[dict]) -> bool:
    """Return True if the QR target is near the center of the frame."""
    if target is None:
        return False

    center = target.get('center') or {}
    frame_width = target.get('frame_width')
    x = center.get('x') if isinstance(center, dict) else None
    if x is None or frame_width is None or frame_width <= 0:
        return False

    left_bound = frame_width / 2.0 - (QR_CENTER_DEADZONE_DEG / MAX_QR_TURN_DEGREE) * (frame_width / 2.0)
    right_bound = frame_width / 2.0 + (QR_CENTER_DEADZONE_DEG / MAX_QR_TURN_DEGREE) * (frame_width / 2.0)
    return left_bound <= x <= right_bound


def should_approach_target(target: Optional[dict]) -> bool:
    """Return True when the QR target is close enough and centered enough to approach."""
    if target is None:
        return False

    area_ratio = target.get('area_ratio')
    if area_ratio is None or area_ratio < QR_APPROACH_AREA_RATIO:
        return False

    center = target.get('center') or {}
    frame_width = target.get('frame_width')
    x = center.get('x') if isinstance(center, dict) else None
    if x is None or frame_width is None or frame_width <= 0:
        return False

    left_bound = frame_width / 3.0
    right_bound = frame_width * 2.0 / 3.0
    return left_bound <= x <= right_bound


def should_activate_trigger_motor(target: Optional[dict]) -> bool:
    """Return True when the trigger motor should run for an enemy target centered in the frame."""
    if target is None:
        return False

    label = target.get('label')
    if label not in {'Enemy', 'BiggerEnemy'}:
        return False

    center = target.get('center') or {}
    frame_width = target.get('frame_width')
    x = center.get('x') if isinstance(center, dict) else None
    if x is None or frame_width is None:
        return False

    left_bound = frame_width / 3.0
    right_bound = frame_width * 2.0 / 3.0
    return left_bound <= x <= right_bound


def decide_motion(detections: Iterable[Any], fallback_direction: str) -> str:
    """Return the final motion direction, preferring detection over roaming."""
    target = select_highest_priority_target(detections)
    if target is not None:
        action = compute_qr_turn_angle(target)
        return action if action is not None else fallback_direction
    return fallback_direction
