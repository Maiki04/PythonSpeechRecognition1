'''Module Docstring'''

import speech_recognition as sr # type: ignore

def audio():
    '''Audio to text'''
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Talk now")
        data = r.recognize_whisper(r.listen(source))
        print(data)

audio()
