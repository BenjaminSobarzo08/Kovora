import asyncio
import base64

import socketio

from services.transcription_service import transcribe_bytes

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
sio_app = socketio.ASGIApp(sio)
transcription_sessions = {}


def _extract_audio_bytes(payload):
    if payload is None:
        return b""

    if isinstance(payload, bytes):
        return payload

    if isinstance(payload, bytearray):
        return bytes(payload)

    if isinstance(payload, str):
        if payload.startswith("data:") and "," in payload:
            payload = payload.split(",", 1)[1]
        return base64.b64decode(payload)

    if isinstance(payload, dict):
        for key in ("audio", "chunk", "data"):
            if key in payload:
                return _extract_audio_bytes(payload[key])

    raise ValueError("Formato de chunk de audio no soportado")


async def _emit_transcription(sid, is_final=False):
    session = transcription_sessions.get(sid)
    if not session or not session["buffer"]:
        return

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        lambda: transcribe_bytes(bytes(session["buffer"]), suffix=session["suffix"]),
    )

    await sio.emit(
        "transcription_result",
        {
            "original": result.get("original", ""),
            "translated": result.get("translated", ""),
            "isFinal": is_final,
        },
        to=sid,
    )


@sio.event
async def connect(sid, environ):
    print(f"Usuario conectado: {sid}")


@sio.event
async def disconnect(sid):
    transcription_sessions.pop(sid, None)
    print(f"Usuario desconectado: {sid}")


@sio.event
async def join(sid, room):
    await sio.enter_room(sid, room)
    print(f"{sid} se unio a la sala {room}")


@sio.event
async def offer(sid, data, room):
    await sio.emit("offer", data, room=room, skip_sid=sid)


@sio.event
async def answer(sid, data, room):
    await sio.emit("answer", data, room=room, skip_sid=sid)


@sio.event
async def ice_candidate(sid, candidate, room):
    await sio.emit("ice-candidate", candidate, room=room, skip_sid=sid)


@sio.event
async def start_transcription(sid, payload=None):
    payload = payload or {}
    transcription_sessions[sid] = {
        "buffer": bytearray(),
        "suffix": payload.get("suffix", ".webm"),
        "chunks_since_emit": 0,
    }
    await sio.emit("transcription_ready", {"ok": True}, to=sid)


@sio.event
async def audio_chunk(sid, payload):
    if sid not in transcription_sessions:
        await start_transcription(sid, payload if isinstance(payload, dict) else None)

    session = transcription_sessions[sid]
    session["buffer"].extend(_extract_audio_bytes(payload))
    session["chunks_since_emit"] += 1

    # Reprocesamos cada varios chunks para devolver texto parcial.
    if session["chunks_since_emit"] >= 8:
        session["chunks_since_emit"] = 0
        await _emit_transcription(sid, is_final=False)


@sio.event
async def end_transcription(sid):
    if sid not in transcription_sessions:
        return

    await _emit_transcription(sid, is_final=True)
    transcription_sessions.pop(sid, None)
