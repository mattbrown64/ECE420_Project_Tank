import os
import shutil
import subprocess




def _has_mpg123() -> bool:
    return shutil.which("mpg123") is not None


def _play_wav_file(file_path):
    subprocess.call(["afplay", file_path])


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



def map_qr_to_music_key(qr_string: str) -> str | None:
    if not qr_string:
        return None

    normalized = qr_string.strip().lower().rstrip("!").replace(" ", "_")
    if normalized == "friend":
        return "friend"
    if normalized == "lover":
        return "lover"
    if normalized == "enemy":
        return "enemy"
    if normalized in {"BiggerEnemy"}:
        return "bigger_enemy"
    return None


def play_correct_music_for_qr(qr_string: str) -> None:
    if qr_string == "Friend!":
        play_file("music/Just Peachy.wav")
    elif qr_string == "Lover!":
        play_file("music/Careless Whisper.mp3")
    elif qr_string == "Enemy!":
        play_file("music/ready for primetime.wav")
    elif qr_string == "BiggerEnemy!":
        play_file("music/thriller.wav")
    else:
        print(f"Music: No specific track for QR code '{qr_string}'. Playing default.")
        play_file("music/Just Peachy.wav")



if __name__ == "__main__":
    map_qr_to_music_key("Friend!")
    play_correct_music_for_qr("Lover!")

