# pylint: disable=broad-exception-caught, global-statement, invalid-name
'''Module Docstring'''

from threading import Thread
import speech_recognition as sr # type: ignore
from flask import Flask, request


app = Flask(__name__)
recognized_text = ""
text_id = 0


def audio_recognition_loop():
    '''audio_recognition_loop'''
    global recognized_text, text_id
    recognizer = sr.Recognizer()

    while True:
        try:
            with sr.Microphone() as source:
                print("Listening for speech...")
                recognized_text = recognizer.recognize_vosk(recognizer.listen(source))
                print(f"Recognized: {recognized_text}")

                text_id += 1
        except Exception as e:
            print(f"Error during recognition: {e}")
            recognized_text = ""


@app.route('/get_text_id', methods=['GET'])
def get_text_id():
    '''Endpoint to retrieve the current text_id'''
    return str(text_id), 200, {'Content-Type': 'text/plain'}


@app.route('/get_text', methods=['GET'])
def get_text():
    '''Endpoint to retrieve the recognized text as plain text.'''
    return recognized_text, 200, {'Content-Type': 'text/plain'}


@app.route('/update_text', methods=['POST'])
def update_text():
    '''Endpoint to manually update recognized text (optional).'''
    global recognized_text
    recognized_text = request.data.decode('utf-8')
    return "success", 200, {'Content-Type': 'text/plain'}


def start_flask():
    '''Starts the Flask server.'''
    app.run(debug=False, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    recognition_thread = Thread(target=audio_recognition_loop)
    recognition_thread.daemon = True
    recognition_thread.start()

    start_flask()
