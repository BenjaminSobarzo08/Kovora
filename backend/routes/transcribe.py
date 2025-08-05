# routes/transcribe.py
from fastapi import APIRouter, UploadFile, File
import whisper
import tempfile

router = APIRouter()
model = whisper.load_model("base")

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        result = model.transcribe(tmp_path)
        return {"text": result["text"]}
    except Exception as e:
        return {"error": str(e)}
