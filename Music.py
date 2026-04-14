import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
import wave
import pygame




AUDIO_SAMPLE_RATE = 44100
AUDIO_VOLUME = 0.3
SUPPORTED_FILE_EXTENSIONS = [".wav", ".mp3"]


BACKGROUND_MUSIC = {
    "friend": "music/Just Peachy.wav", 
    "lover": "music/Careless Whisper.mp3", 
    "enemy": "music/ready for primetime.wav",  
    "bigger_enemy": "music/thriller.wav",  
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


if __name__ == "__main__":
    main()
