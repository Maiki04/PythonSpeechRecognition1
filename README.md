# SpeechToText

## Overview

This script implements a speech recognition service that listens for audio input and provides recognized text through a FastAPI-based web server. It uses a speech recognition engine (default: Vosk) to continuously process speech from the microphone and updates the recognized text in real time.

The FastAPI server offers multiple endpoints for connectivity, including WebSocket support for real-time updates to connected clients.

The script runs the speech recognition loop in a separate thread, allowing it to continuously capture speech while the server handles API requests and WebSocket connections concurrently.

## Instructions

**Warning:** Do not use with `Python 3.13`, as most plugins are not yet compatible. Instead, use `Python 3.11` or `3.12`.  
  I personally use `3.12.8` at the moment.

### How to run

... if you have multiple python installations (and the default installation is not `3.12`):

- In your terminal locate the `Python312` folder.  
  For me it's: `C:\Users\Admin\AppData\Local\Programs\Python\Python312`

**Make sure the terminal runs on this folder!**

- In the terminal run: `python.exe -m pip install RequiredPackageNameHere`  
  Refer to the package section below.

- In `VSCode` or your editor of choice open a terminal (doesn't need to be on the `Python312` folder path.)  
  and run: `py -V:3.12 .\speech_to_text.py`

**OR (Recommended)** you can setup a venv (virtual environment) based on your python `3.12` installation.

**OR** you can switch the global installation by going into the windows enviroment variables and changing the entries

- `C:\Users\Admin\AppData\Local\Programs\Python\Python313\Scripts\`

and

- `C:\Users\Admin\AppData\Local\Programs\Python\Python313\`

in the system (variable) path to use `Python312` (make sure python `3.12` is installed).

---

When you want to **target a different Vosk model** for speech recognition just change the `vosk_model_path` path in the corresponding config.json (example: `keyword_recognition_config.json`).

You can download additional Vosk models from [https://alphacephei.com/vosk/models](https://alphacephei.com/vosk/models).

### Required Packages

**Important:**  
  _Check the requirements.txt for a detailed overview!_

- **[PyAudio](https://pypi.org/project/PyAudio/)**  
  PyAudio provides Python bindings for PortAudio v19, the cross-platform audio I/O library.

- **[soundfile](https://pypi.org/project/soundfile/)**  
  Library for reading and writing sound files.

- **[uvicorn](https://pypi.org/project/uvicorn/)**  
  Uvicorn is an ASGI web server implementation for Python.

- **[fastapi](https://pypi.org/project/fastapi/)**  
  FastAPI is a modern, high-performance, web framework for building APIs with Python based on standard Python type hints.

- **[Levenshtein](https://pypi.org/project/Levenshtein/)**  
  Levenshtein is a string metric that measures the minimum number of single-character edits (insertions, deletions, etc.).
  In STT the package is useful for implementing fuzzy matching to account for mispronunciations or transcription errors in keyword detection.

---

Depending on the model(s) you want to use, not all of these packages may be required. Select the ones you need.

- **[vosk](https://pypi.org/project/vosk/)** (Recommended!)  
  Vosk is an offline open source speech recognition toolkit.

- **[tensorflow](https://pypi.org/project/tensorflow/)**  
  TensorFlow is an open source software library for high performance numerical computation.

- **openai-whisper**

  - **[torch](https://pypi.org/project/torch/)**  
    PyTorch, a deep learning framework.

  - **[whisper](https://pypi.org/project/whisper/)** (Not sure if required!)  
    A text-to-speech library.

  - **[openai-whisper](https://pypi.org/project/openai-whisper/)**  
    OpenAI's Whisper model for speech-to-text transcription.

## Sources

### Speech recognition in python (great for general learning)

- [https://realpython.com/python-speech-recognition/](https://realpython.com/python-speech-recognition/)
- [https://www.simplilearn.com/tutorials/python-tutorial/speech-recognition-in-python](https://www.simplilearn.com/tutorials/python-tutorial/speech-recognition-in-python)
- [https://medium.com/naukri-engineering/speech-recognition-in-python-fcda027a97a1](https://medium.com/naukri-engineering/speech-recognition-in-python-fcda027a97a1)
