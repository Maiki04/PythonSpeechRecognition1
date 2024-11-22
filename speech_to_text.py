# pylint: disable=broad-exception-caught, global-statement, invalid-name, line-too-long, missing-function-docstring, multiple-statements
'''Module Docstring'''

from asyncio import run as asyncio_run
from json import load as json_load, loads as json_loads
from threading import Thread
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
import speech_recognition as sr  # type: ignore
import uvicorn


app = FastAPI()

# Shared state
recognized_text = ""


def load_config(config_path: str):
    """Load configuration from a JSON file."""
    with open(config_path, 'r', encoding='utf-8') as file:
        return json_load(file)


# WebSocket connection manager
class ConnectionManager:
    '''Manages WebSocket connections.'''
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        '''Sends a message to all connected WebSocket clients.'''
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                self.disconnect(connection)


manager = ConnectionManager()


def audio_recognition_loop(config_path="keyword_recognition_config.json"):
    '''audio_recognition_loop'''
    global recognized_text
    recognizer = sr.Recognizer()

    config = load_config(config_path)

    with sr.Microphone(sample_rate=config["microphone"]["sample_rate"], chunk_size=config["microphone"]["chunk_size"]) as source:
        # Optional adjustment for filtering ambient noise
        print("Adjusting for ambient noise, please don't talk...")
        recognizer.adjust_for_ambient_noise(source, duration=config["recognizer"]["adjust_for_ambient_noise_duration"])

        recognizer.energy_threshold = config["recognizer"]["energy_threshold"] # Sensitivity for picking up audio
        recognizer.pause_threshold  = config["recognizer"]["pause_threshold"]

        while True:
            try:
                print("Listening for speech...")
                # Adjust phrase_time_limit for shorter audio chunks
                audio = recognizer.listen(source, phrase_time_limit=config["recognizer"]["phrase_time_limit"])
                recognized_text = recognizer.recognize_vosk(audio, language=config["ai"]["language"])
                recognized_text = json_loads(recognized_text)["text"]

                print(f"Recognized: {recognized_text}")

                # Notify WebSocket clients
                asyncio_run(manager.broadcast(recognized_text))

            except Exception as e:
                print(f"Error during recognition: {e}")
                recognized_text = ""


@app.get('/get_text', response_class=PlainTextResponse)
async def get_text():
    '''Endpoint to retrieve the recognized text as plain text.'''
    return recognized_text


@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    '''WebSocket endpoint for real-time updates.'''
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == '__main__':
    recognition_thread = Thread(target=audio_recognition_loop)
    recognition_thread.daemon = True
    recognition_thread.start()

    uvicorn.run(app, host='0.0.0.0', port=5000)
