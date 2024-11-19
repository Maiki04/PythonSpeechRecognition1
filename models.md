# Models

## Current Default

- OpenAI Whisper
  - **Pros**: High accuracy, supports multiple languages, open source.
  - **Cons**: Computationally intensive and slower on standard hardware.

## Best Case ?

- Vosk (Offline): Lightweight and efficient, with excellent real-time performance on local devices.
  - **Pros**: Lightweight, efficient, works offline, supports many languages.
  - **Cons**: Slightly lower accuracy for complex speech than Whisper.

- Google Cloud Speech-to-Text (Online): Fast and accurate for rapid-fire commands.
  - **Pros**: Fast, highly accurate, supports real-time streaming.
  - **Cons**: Requires an internet connection and incurs usage costs.

- TensorFlow (Custom Models): Tailored keyword recognition but requires investment in development.
  - **Pros**: Highly customizable, can be optimized for specific use cases like keyword spotting.
  - **Cons**: Requires extensive training and setup; performance depends on the model used.

- Houndify: Optimized for real-time, voice-controlled applications.
  - **Pros**: Real-time processing optimized for voice commands.
  - **Cons**: Requires an internet connection; less widespread use.

## Others

- Wit: Free for small-scale use, focuses on intent and entity recognition.
- AssemblyAI
