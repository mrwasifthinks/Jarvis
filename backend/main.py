import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from socketio import AsyncServer, ASGIApp
from dotenv import load_dotenv
from fastapi import File, UploadFile
from backend.core.voice_processing import VoiceProcessor
from backend.utils.error_handler import error_handler

# Load environment variables
load_dotenv()

# Initialize FastAPI app
fastapi_app = FastAPI(
    title="JARVIS AI Assistant",
    description="A desktop-based virtual assistant inspired by Iron Man's JARVIS",
    version="0.1.0"
)

# Configure CORS for frontend communication
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:*",
    "http://localhost:*",
    "http://127.0.0.1:49928"
]

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Socket.IO with proper CORS configuration
sio = AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=allowed_origins,
    logger=True,
    engineio_logger=True
)

# Mount FastAPI app to Socket.IO
app = ASGIApp(sio, fastapi_app)

# Socket.IO event handlers
@sio.on('connect')
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.on('disconnect')
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.on('message')
async def message(sid, data):
    print(f"Message from {sid}: {data}")
    await sio.emit('message', {'response': 'Message received'}, room=sid)

# WebSocket routes will be handled by Socket.IO

# WebSocket connection for real-time communication
# Root endpoint
@fastapi_app.get("/")
async def root():
    return {"message": "Welcome to JARVIS AI Assistant API"}

# Health check endpoint
@fastapi_app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Weather endpoint
@fastapi_app.get("/api/weather")
async def get_weather():
    try:
        # Mock weather data for demonstration
        weather_data = {
            "temperature": 25,
            "condition": "Sunny",
            "humidity": 60,
            "wind_speed": 10
        }
        return weather_data
    except Exception as e:
        return {"error": str(e)}, 500

# Import and include API routers
# These will be implemented as we develop the specific modules
# from .api.voice import router as voice_router
# from .api.command import router as command_router
# from .api.ai import router as ai_router
# from .api.system import router as system_router

# app.include_router(voice_router, prefix="/api/voice", tags=["Voice"])
# app.include_router(command_router, prefix="/api/command", tags=["Command"])
# app.include_router(ai_router, prefix="/api/ai", tags=["AI"])
# app.include_router(system_router, prefix="/api/system", tags=["System"])

# Run the application with uvicorn when executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# Initialize VoiceProcessor with default config
voice_processor = VoiceProcessor({"wake_word": "Hey JARVIS"})

@fastapi_app.post("/api/process_voice")
async def process_voice(audio_file: UploadFile = File(...)):
    try:
        # Read the audio data
        audio_data = await audio_file.read()
        
        # Process the voice input
        transcribed_text = await voice_processor.process_voice_input(audio_data)
        
        if not transcribed_text:
            return {"error": "Could not transcribe audio", "status": "error"}
        
        return {
            "status": "success",
            "text": transcribed_text
        }
    except Exception as e:
        error_data = error_handler.log_error(e, {"endpoint": "/api/process_voice"})
        return error_data