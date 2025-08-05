import socketio

sio = socketio.AsyncServer(cors_allowed_origins="*")
sio_app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ):
    print(f"🟢 Usuario conectado: {sid}")

@sio.event
async def disconnect(sid):
    print(f"🔴 Usuario desconectado: {sid}")

@sio.event
async def join(sid, room):
    sio.enter_room(sid, room)
    print(f"👥 {sid} se unió a la sala {room}")

@sio.event
async def offer(sid, data, room):
    await sio.emit("offer", data, room=room, skip_sid=sid)

@sio.event
async def answer(sid, data, room):
    await sio.emit("answer", data, room=room, skip_sid=sid)

@sio.event
async def ice_candidate(sid, candidate, room):
    await sio.emit("ice-candidate", candidate, room=room, skip_sid=sid)
