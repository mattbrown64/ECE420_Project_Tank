import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
import wave
import pygame

"""Music module for Raspberry Pi and amplified speaker scenarios.

This module generates simple tone sequences and plays them with Linux 'aplay'.
Use a Raspberry Pi audio output or a line-level amplifier input for Amplified Speaker 2.
For Arduino, reuse the same note-frequency sequences in an Arduino 'tone()' sketch.
"""

NOTE_FREQUENCIES = {
    "C4": 261.63,
    "D4": 293.66,
    "E4": 329.63,
    "F4": 349.23,
    "G4": 392.00,
    "A4": 440.00,
    "B4": 493.88,
    "C5": 523.25,
    "D5": 587.33,
    "E5": 659.25,
    "F5": 698.46,
    "G5": 783.99,
    "A5": 880.00,
}

SCENARIOS = {
    "startup": [
        (NOTE_FREQUENCIES["C4"], 200),
        (NOTE_FREQUENCIES["E4"], 200),
        (NOTE_FREQUENCIES["G4"], 200),
        (NOTE_FREQUENCIES["C5"], 300),
    ],
    "alert": [
        (NOTE_FREQUENCIES["G4"], 120),
        (NOTE_FREQUENCIES["G4"], 120),
        (NOTE_FREQUENCIES["F4"], 120),
        (NOTE_FREQUENCIES["F4"], 120),
        (NOTE_FREQUENCIES["G4"], 120),
    ],
    "victory": [
        (NOTE_FREQUENCIES["C5"], 180),
        (NOTE_FREQUENCIES["B4"], 180),
        (NOTE_FREQUENCIES["A4"], 180),
        (NOTE_FREQUENCIES["G4"], 180),
        (NOTE_FREQUENCIES["E5"], 300),
    ],
}

AUDIO_SAMPLE_RATE = 44100
AUDIO_VOLUME = 0.3
SUPPORTED_FILE_EXTENSIONS = [".wav", ".mp3"]

# Background music paths - update these with your actual file paths
BACKGROUND_MUSIC = {
    "friend": "music/Just Peachy.wav",  # Replace with actual path
    "lover": "music/Careless Whisper.mp3",  # Replace with actual path
    "enemy": "music/ready for primetime.wav",  # Replace with actual path
    "bigger_enemy": "music/thriller.wav",  # Replace with actual path
}

_current_music = None
_pygame_initialized = False


def _has_aplay() -> bool:
    return shutil.which("aplay") is not None


def _has_mpg123() -> bool:
    return shutil.which("mpg123") is not None

def _init_pygame():
    global _pygame_initialized
    if not _pygame_initialized:
        pygame.init()
        pygame.mixer.music.set_volume(AUDIO_VOLUME)
        _pygame_initialized = True


def _play_wav_file(path: str) -> None:
    if not _has_aplay():
        print("Music: 'aplay' is not available. Install it with 'sudo apt install alsa-utils'.")
        return

    try:
        subprocess.run(["aplay", "-q", path], check=True)
    except subprocess.CalledProcessError:
        print(f"Music: failed to play WAV file '{path}'.")


def _play_mp3_file(path: str) -> None:
    if not _has_mpg123():
        print("Music: 'mpg123' is not available. Install it with 'sudo apt install mpg123'.")
        return

    try:
        subprocess.run(["mpg123", "-q", path], check=True)
    except subprocess.CalledProcessError:
        print(f"Music: failed to play MP3 file '{path}'.")


def play_file(path: str) -> None:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Music file not found: {path}")

    ext = os.path.splitext(path)[1].lower()
    if ext == ".wav":
        _play_wav_file(path)
    elif ext == ".mp3":
        _play_mp3_file(path)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Supported: {SUPPORTED_FILE_EXTENSIONS}")

def play_background_music(detection_type: str) -> None:
    global _current_music
    if detection_type not in BACKGROUND_MUSIC:
        return

    music_path = BACKGROUND_MUSIC[detection_type]
    if not os.path.isfile(music_path):
        print(f"Music: background music file not found: {music_path}")
        return

    _init_pygame()

    if _current_music == detection_type:
        # Already playing this music, continue
        return

    # Fade out current music if playing
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.fadeout(1000)  # 1 second fade out
        time.sleep(1.1)  # Wait for fade out

    # Load and play new music with fade in
    try:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1, fade_ms=1000)  # Loop indefinitely with 1 second fade in
        _current_music = detection_type
    except pygame.error as e:
        print(f"Music: failed to play background music '{music_path}': {e}")

def stop_background_music() -> None:
    global _current_music
    _init_pygame()
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.fadeout(1000)
        time.sleep(1.1)
    _current_music = None


def _generate_wave_data(frequency: float, duration_ms: int, volume: float = AUDIO_VOLUME) -> bytes:
    frame_count = int(AUDIO_SAMPLE_RATE * duration_ms / 1000)
    amplitude = int(32767 * volume)
    data = bytearray()

    for i in range(frame_count):
        sample = amplitude * math.sin(2.0 * math.pi * frequency * i / AUDIO_SAMPLE_RATE)
        data += int(sample).to_bytes(2, byteorder="little", signed=True)
    return bytes(data)


def _play_wav_bytes(wav_data: bytes) -> None:
    if not _has_aplay():
        print("Music: 'aplay' is not available. Install it on Raspberry Pi with 'sudo apt install alsa-utils'.")
        return

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp_file.write(wav_data)
        temp_path = tmp_file.name

    try:
        subprocess.run(["aplay", "-q", temp_path], check=True)
    except subprocess.CalledProcessError:
        print("Music: failed to play WAV data with aplay.")
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass


def _build_wav(frequency: float, duration_ms: int) -> bytes:
    wave_data = _generate_wave_data(frequency, duration_ms)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        with wave.open(tmp_file, "wb") as wave_file:
            wave_file.setnchannels(1)
            wave_file.setsampwidth(2)
            wave_file.setframerate(AUDIO_SAMPLE_RATE)
            wave_file.writeframes(wave_data)
        temp_path = tmp_file.name

    with open(temp_path, "rb") as f:
        wav_bytes = f.read()

    os.remove(temp_path)
    return wav_bytes


def _play_note(frequency: float, duration_ms: int) -> None:
    if frequency <= 0 or duration_ms <= 0:
        time.sleep(duration_ms / 1000.0)
        return

    wave_bytes = _build_wav(frequency, duration_ms)
    _play_wav_bytes(wave_bytes)


def play_sequence(sequence: list[tuple[float, int]], pause_ms: int = 80) -> None:
    for frequency, duration in sequence:
        _play_note(frequency, duration)
        time.sleep(pause_ms / 1000.0)


def play_scenario(name: str) -> None:
    if name not in SCENARIOS:
        raise ValueError(f"Unknown scenario '{name}'. Valid options: {', '.join(SCENARIOS)}")
    play_sequence(SCENARIOS[name])


def play_startup() -> None:
    play_scenario("startup")


def play_alert() -> None:
    play_scenario("alert")


def play_victory() -> None:
    play_scenario("victory")


def main() -> None:
    print("Music module for Raspberry Pi / amplified speaker scenarios")
    print("Usage: python Music.py [startup|alert|victory]")
    print("       python Music.py /path/to/file.wav")
    print("       python Music.py /path/to/file.mp3")
    if len(sys.argv) == 2:
        arg = sys.argv[1]
        if os.path.isfile(arg):
            play_file(arg)
            return

        scenario = arg.lower()
        if scenario not in SCENARIOS:
            print("Unknown scenario or file path.")
            sys.exit(1)
        play_scenario(scenario)
    else:
        print("Playing all three scenarios in order...")
        play_startup()
        play_alert()
        play_victory()


if __name__ == "__main__":
    main()
