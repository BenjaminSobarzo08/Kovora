from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

from routes import transcribe
from sockets import sio

fastapi_app = FastAPI()

# CORS para permitir conexiones del frontend (Vite)
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fastapi_app.include_router(transcribe.router)

# Exportamos una sola app ASGI que atiende HTTP y Socket.IO
app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app, socketio_path="socket.io")
