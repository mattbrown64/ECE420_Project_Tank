# ECE420 Tank (Raspberry Pi)

## Target Platform
- Raspberry Pi 4/5
- Raspberry Pi OS Bookworm (64-bit)
- Python 3.10+

## Install (on Pi)
```bash
sudo apt update
sudo apt install -y python3-venv python3-pip python3-lgpio

cd /Users/mattbrown/Documents/Github/ECE420_Project_Tank
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## GPIO Configuration
Defaults used by the app:
- Trigger: `18`
- Forward echo: `17`
- Left echo: `27`
- Right echo: `22`
- Threshold (cm): `5`

## Run
```bash
source .venv/bin/activate
python main.py
```

Stop with `Ctrl+C`.

## Notes
- Movement logic is now handled in `motor.py` and the main control flow, not in a separate `move.py` stub.
- This update focuses on Raspberry Pi runtime compatibility and sensor loop reliability.
- For test environments without a Pi camera, set `CAMERA_TEST_IMAGE` to a saved image path before running `main.py`.
