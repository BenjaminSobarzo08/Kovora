from fastapi import APIRouter, File, UploadFile

from services.transcription_service import transcribe_bytes

router = APIRouter()


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()
        suffix = ".webm"
        if file.filename and "." in file.filename:
            suffix = f".{file.filename.rsplit('.', 1)[-1]}"

        return transcribe_bytes(audio_bytes, suffix=suffix)
    except Exception as e:
        return {"error": str(e)}
