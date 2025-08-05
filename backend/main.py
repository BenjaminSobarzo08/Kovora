from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sockets import sio_app
from fastapi.middleware.wsgi import WSGIMiddleware
from routes import transcribe

app = FastAPI()

# CORS para permitir conexiones del frontend (Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montamos la app Socket.IO junto con FastAPI
app.include_router(transcribe.router)
app.mount("/", WSGIMiddleware(sio_app))
