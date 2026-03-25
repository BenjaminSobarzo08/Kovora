import os
import tempfile
from functools import lru_cache

import whisper

SOURCE_LANG = "es"
TARGET_LANG = "en"


@lru_cache(maxsize=1)
def get_model():
    return whisper.load_model("base")


def _transcribe_file(path: str) -> dict:
    model = get_model()
    original = model.transcribe(path, language=SOURCE_LANG, task="transcribe")

    translated_text = ""
    if TARGET_LANG == "en":
        translated = model.transcribe(path, language=SOURCE_LANG, task="translate")
        translated_text = translated.get("text", "").strip()

    return {
        "original": original.get("text", "").strip(),
        "translated": translated_text,
    }


def transcribe_bytes(audio_bytes: bytes, suffix: str = ".webm") -> dict:
    if not audio_bytes:
        return {"original": "", "translated": ""}

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        return _transcribe_file(tmp_path)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
