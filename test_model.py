# pylint: disable=missing-function-docstring, missing-module-docstring, line-too-long, broad-exception-caught
import numpy as np
import librosa
import keras  # type: ignore

# Configuration
MODEL_PATH = 'customModel/best_model.h5'

KEYWORDS = ["left", "right", "up", "down", "pause", "continue", "restart", "quit"]
SAMPLE_RATE = 16000
DURATION = 1
N_MFCC = 40


def load_audio(file_path, sr=SAMPLE_RATE, duration=DURATION):
    """Load a WAV file and ensure it is of fixed duration."""
    signal, _ = librosa.load(file_path, sr=sr)
    signal = librosa.util.fix_length(signal, size=sr * duration)
    return signal


def extract_features(signal, sr=SAMPLE_RATE, n_mfcc=N_MFCC, fixed_length=96):
    """Extract normalized MFCC features from the audio signal."""
    mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=n_mfcc)

    if mfcc.shape[1] < fixed_length:
        mfcc = np.pad(mfcc, ((0, 0), (0, fixed_length - mfcc.shape[1])), mode='constant')
    else:
        mfcc = mfcc[:, :fixed_length]

    mfcc = (mfcc - np.mean(mfcc)) / (np.std(mfcc) + 1e-10)
    return np.expand_dims(mfcc, axis=-1)


def main():
    model = keras.models.load_model(MODEL_PATH)

    wav_file = 'dataset/right/right (16).wav'

    signal = load_audio(wav_file)
    features = extract_features(signal)

    features = np.expand_dims(features, axis=0)

    predictions = model.predict(features)
    predicted_index = np.argmax(predictions)
    predicted_keyword = KEYWORDS[predicted_index]

    print(f"Predicted keyword: {predicted_keyword}")


if __name__ == "__main__":
    main()
