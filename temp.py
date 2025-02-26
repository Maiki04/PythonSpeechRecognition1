# pylint: disable=broad-exception-caught, global-statement, invalid-name, line-too-long, missing-function-docstring, missing-module-docstring, multiple-statements
import keras # type: ignore
import numpy as np
import librosa

def custom_model_recognition(audio_queue, result_queue):
    model = keras.models.load_model("customModel/best_model.h5")

    # Define keywords (make sure these match the order used during training)
    KEYWORDS = ["left", "right", "up", "down"]

    SAMPLE_RATE = 16000 #config["general"]["sample_rate"]
    N_MFCC = 40
    bytes_per_second = SAMPLE_RATE * 2

    # A buffer to accumulate audio data from the queue.
    audio_buffer = bytes()

    while True:
        audio_chunk = audio_queue.get()
        audio_buffer += audio_chunk

        # If we have at least 1 second of audio, process it.
        if len(audio_buffer) >= bytes_per_second:
            # Extract exactly one second of audio.
            clip = audio_buffer[:bytes_per_second]
            # Remove the processed bytes from the buffer.
            audio_buffer = audio_buffer[bytes_per_second:]

            # Convert raw bytes to a numpy array.
            # pyaudio streams in 16-bit PCM data.
            signal = np.frombuffer(clip, dtype=np.int16).astype(np.float32) / 32768.0
            # Ensure the signal is exactly one second long.
            signal = librosa.util.fix_length(signal, size=SAMPLE_RATE)

            # Extract MFCC features.
            mfcc = librosa.feature.mfcc(y=signal, sr=SAMPLE_RATE, n_mfcc=N_MFCC)
            # Optionally, apply the same normalization used in training.
            mfcc = (mfcc - np.mean(mfcc)) / (np.std(mfcc) + 1e-10)
            mfcc = np.expand_dims(mfcc, axis=-1)
            mfcc = np.expand_dims(mfcc, axis=0)

            # Predict using model.
            predictions = model.predict(mfcc)
            predicted_index = np.argmax(predictions)
            command = KEYWORDS[predicted_index]

            print(f"Model predicted: {command}")
            result_queue.put(command)
