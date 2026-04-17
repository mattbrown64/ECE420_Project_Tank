import os
from typing import Dict, Optional

import qrcode

PRIORITY_QR_CODES = ["BiggerEnemy", "Friend", "Enemy", "Lover"]

QR_PAYLOADS: Dict[str, str] = {
    "BiggerEnemy": "BiggerEnemy!",
    "Friend": "Friend!",
    "Enemy": "Enemy!",
    "Lover": "Lover!",
}

KNOWN_QR_LOOKUP: Dict[str, str] = {
    raw_value: label for label, raw_value in QR_PAYLOADS.items()
}
KNOWN_QR_LOOKUP.update({label: label for label in QR_PAYLOADS})

SIMPLIFIED_QR_LOOKUP: Dict[str, str] = {}
for raw_value, label in KNOWN_QR_LOOKUP.items():
    simplified = "".join(ch for ch in raw_value if ch.isalnum()).lower()
    if simplified:
        SIMPLIFIED_QR_LOOKUP[simplified] = label


def normalize_qr_label(value: str) -> Optional[str]:
    if not isinstance(value, str):
        return None

    cleaned = value.strip()
    if cleaned in KNOWN_QR_LOOKUP:
        return KNOWN_QR_LOOKUP[cleaned]

    simplified = "".join(ch for ch in cleaned if ch.isalnum()).lower()
    return SIMPLIFIED_QR_LOOKUP.get(simplified)


def generate_qr_images(output_dir: str = ".") -> None:
    os.makedirs(output_dir, exist_ok=True)
    for label, payload in QR_PAYLOADS.items():
        output_path = os.path.join(output_dir, f"qrcode_{label.lower()}.png")
        code = qrcode.make(payload)
        code.save(output_path)


if __name__ == "__main__":
    generate_qr_images()
