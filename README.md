# ECE420 Tank (Raspberry Pi)

## Target Platform
- Raspberry Pi 4/5
- Raspberry Pi OS Bookworm (64-bit)
- Python 3.10+

## Install (on Pi)
```bash
sudo apt update
sudo apt install -y python3-venv python3-pip python3-lgpio alsa-utils mpg123

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

## Background Music
Place your music files in the `music/` directory with these names:
- `Just Peachy.wav` (for friend detection / default)
- `Careless Whisper.mp3` (for lover detection)
- `ready for primetime.wav` (for enemy detection)
- `thriller.wav` (for bigger enemy detection)

Music transitions smoothly between detections with 1-second fade in/out.

## Run
```bash
source .venv/bin/activate
python main.py
```

Stop with `Ctrl+C`.

## Notes
- Movement logic in `move.py` is still a software stub and does not drive motors yet.
- This update focuses on Raspberry Pi runtime compatibility and sensor loop reliability.
