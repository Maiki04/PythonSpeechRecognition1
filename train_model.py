# pylint: disable=missing-function-docstring, missing-module-docstring, line-too-long, broad-exception-caught
import os
import numpy as np
import librosa
import librosa.display
import tensorflow as tf  # type: ignore
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split  # type: ignore
from keras import layers, models, optimizers, callbacks  # type: ignore
from keras.utils import to_categorical  # type: ignore # pylint: disable=import-error

# CONFIGURATION
DATASET_PATH = "dataset/"
MODEL_DIR = "customModel"
MODEL_PATH = os.path.join(MODEL_DIR, "keyword_model.h5")
KEYWORDS = ["left", "right", "up", "down"]
SAMPLE_RATE = 16000
DURATION = 3  # 3-second clips
N_MFCC = 40  # Number of MFCC features
BATCH_SIZE = 32
EPOCHS = 50
AUGMENTATION = True  # Data augmentation toggle

# Check for GPU availability
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

# ------------------------------
# DATA LOADING & PREPROCESSING
# ------------------------------
def load_audio_files(dataset_path):
    raw_signals, raw_labels = [], []
    for idx, keyword in enumerate(KEYWORDS):
        keyword_path = os.path.join(dataset_path, keyword)
        for file in os.listdir(keyword_path):
            file_path = os.path.join(keyword_path, file)
            try:
                signal, _ = librosa.load(file_path, sr=SAMPLE_RATE)
                # Fix length to 1 second (pad or trim)
                signal = librosa.util.fix_length(signal, size=SAMPLE_RATE * DURATION)
                raw_signals.append(signal)
                raw_labels.append(idx)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    return np.array(raw_signals), np.array(raw_labels)

def extract_features(signal):
    mfcc = librosa.feature.mfcc(y=signal, sr=SAMPLE_RATE, n_mfcc=N_MFCC)
    return mfcc

def augment_audio(signal):
    noise = np.random.randn(len(signal)) * 0.005
    signal_noisy = signal + noise  # Add noise
    time_stretched = librosa.effects.time_stretch(signal_noisy, rate=np.random.uniform(0.8, 1.2))
    time_stretched = librosa.util.fix_length(time_stretched, size=len(signal))
    pitch_shifted = librosa.effects.pitch_shift(time_stretched, sr=SAMPLE_RATE, n_steps=np.random.randint(-2, 3))
    pitch_shifted = librosa.util.fix_length(pitch_shifted, size=len(signal))
    return pitch_shifted

def augment_dataset(raw_signals, raw_labels):
    augmented_signals, augmented_labels = [], []
    for i, signal in enumerate(raw_signals):
        augmented_signals.append(signal)
        augmented_labels.append(raw_labels[i])
        # Add augmented version
        augmented_signals.append(augment_audio(signal))
        augmented_labels.append(raw_labels[i])
    return np.array(augmented_signals), np.array(augmented_labels)

# ------------------------------
# MODEL DEFINITION (CNN + LSTM)
# ------------------------------
def build_model(input_shape, n_classes):
    model = models.Sequential([
        layers.Conv2D(32, (3, 3), activation="relu", input_shape=input_shape),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation="relu"),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(128, (3, 3), activation="relu"),
        layers.MaxPooling2D((2, 2)),
        # Reshape for LSTM: keep the MFCC dimension and flatten remaining dimensions
        layers.Reshape((input_shape[0], -1)),
        layers.LSTM(64, return_sequences=True),
        layers.LSTM(64),
        layers.Dense(128, activation="relu"),
        layers.Dropout(0.3),
        layers.Dense(n_classes, activation="softmax")
    ])
    model.compile(optimizer=optimizers.Adam(learning_rate=0.001),
                  loss="categorical_crossentropy",
                  metrics=["accuracy"])
    return model

# ------------------------------
# MAIN FUNCTION
# ------------------------------
def main():
    # 1. Load raw audio signals and labels
    raw_signals, raw_labels = load_audio_files(DATASET_PATH)
    print(f"Loaded {len(raw_signals)} audio files.")

    # 2. Data augmentation (if enabled)
    if AUGMENTATION:
        raw_signals, raw_labels = augment_dataset(raw_signals, raw_labels)
        print(f"After augmentation, dataset size: {len(raw_signals)}")

    # 3. Extract MFCC features
    features = np.array([extract_features(signal) for signal in raw_signals])

    # 4. Normalize features (global normalization)
    mean = np.mean(features, axis=0)
    std = np.std(features, axis=0)
    features = (features - mean) / (std + 1e-10)

    # 5. Expand dims for channel (needed for CNN input)
    features = np.expand_dims(features, axis=-1)

    # 6. Convert labels to one-hot encoding
    onehot_labels = to_categorical(raw_labels, num_classes=len(KEYWORDS))

    # 7. Split dataset into training and testing sets
    x_train, x_test, y_train, y_test = train_test_split(features, onehot_labels, test_size=0.2, random_state=42)

    # 8. Build model
    local_input_shape = (features.shape[1], features.shape[2], 1)
    local_model = build_model(input_shape=local_input_shape, n_classes=len(KEYWORDS))
    local_model.summary()

    # 9. Define callbacks
    early_stopping = callbacks.EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)
    reduce_lr = callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, verbose=1)
    checkpoint = callbacks.ModelCheckpoint(filepath=os.path.join(MODEL_DIR, "best_model.h5"),
                                             monitor="val_loss", save_best_only=True, verbose=1)
    tensorboard = callbacks.TensorBoard(log_dir="logs", histogram_freq=1)
    csv_logger = callbacks.CSVLogger("training_log.csv")

    # 10. Train the model
    history = local_model.fit(x_train, y_train, epochs=EPOCHS, batch_size=BATCH_SIZE,
                              validation_data=(x_test, y_test),
                              callbacks=[early_stopping, reduce_lr, checkpoint, tensorboard, csv_logger])

    # 11. Save the final model
    os.makedirs(MODEL_DIR, exist_ok=True)
    local_model.save(MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

    # 12. Plot training results (accuracy and loss)
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.plot(history.history["accuracy"], label="Train Accuracy")
    plt.plot(history.history["val_accuracy"], label="Validation Accuracy")
    plt.xlabel("Epochs")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.title("Model Accuracy")

    plt.subplot(1, 2, 2)
    plt.plot(history.history["loss"], label="Train Loss")
    plt.plot(history.history["val_loss"], label="Validation Loss")
    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.legend()
    plt.title("Model Loss")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
