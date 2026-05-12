'''Main application for real-time speech emotion recognition using Gradio.'''

import os
import pickle
import numpy as np
import gradio as gr

from feature_extraction import extract_features
from utils import convert_to_wav
from config import MODEL_PATH, SCALER_PATH

# =========================
# LOAD MODEL ONCE AT STARTUP
# =========================

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

with open(SCALER_PATH, "rb") as f:
    scaler = pickle.load(f)


EMOTION_EMOJI = {
    "neutral": "😐",
    "happy":   "😄",
    "sad":     "😢",
    "angry":   "😠",
}


# =========================
# INFERENCE
# =========================

def predict_emotion(audio_path):
    """
    Runs inference on a WAV file.
    Returns (emotion: str, confidence: float, prob_dict: dict)
    Always 3 values — never crashes the caller.
    """

    features = extract_features(audio_path)

    if features is None:
        return "Error: feature extraction failed", 0.0, {}

    features = np.array(features, dtype=np.float64)

    if not np.all(np.isfinite(features)):
        return "Error: invalid features (NaN/inf)", 0.0, {}

    features = np.expand_dims(features, axis=0)
    features = scaler.transform(features)

    probabilities = model.predict_proba(features)[0]
    idx = np.argmax(probabilities)

    emotion = model.classes_[idx]
    confidence = float(probabilities[idx] * 100)

    prob_dict = {
        cls: float(prob * 100)
        for cls, prob in zip(model.classes_, probabilities)
    }

    return emotion, confidence, prob_dict


# =========================
# GRADIO HANDLER
# =========================

def process_file(file_path):

    if file_path is None:
        return "No file uploaded", "—", {}

    # Gradio 4.x returns a filepath string, 3.x returns object with .name
    input_path = file_path if isinstance(file_path, str) else file_path.name

    # Convert to WAV only if needed
    if not input_path.lower().endswith(".wav"):
        wav_path = convert_to_wav(input_path)
        if wav_path is None:
            return "FFmpeg conversion failed", "—", {}
        converted = True
    else:
        wav_path = input_path
        converted = False

    try:
        emotion, confidence, probs = predict_emotion(wav_path)

        if emotion.startswith("Error"):
            return emotion, "—", {}

        emoji = EMOTION_EMOJI.get(emotion, "")
        emotion_display = f"{emoji}  {emotion.capitalize()}"
        confidence_display = f"{confidence:.2f}%"

        # gr.Label expects 0–1 floats, not percentages
        probs_normalized = {k: v / 100.0 for k, v in probs.items()}

        return emotion_display, confidence_display, probs_normalized

    finally:
        # Only clean up the temp wav we created, not the original file
        if converted and wav_path and os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except Exception:
                pass


# =========================
# INTERFACE
# =========================

with gr.Blocks(title="Speech Emotion Recognition") as interface:

    gr.Markdown(
        """
        # 🎙️ Speech Emotion Recognition
        Upload any audio or video file. The system extracts speech features and predicts one of **4 emotions**: Neutral, Happy, Sad, Angry.
        """
    )

    with gr.Row():

        with gr.Column(scale=1):
            audio_input = gr.File(
                label="Upload Audio / Video File",
                file_types=[".wav", ".mp3", ".mp4", ".mkv", ".flac", ".ogg", ".m4a", ".webm"]
            )
            submit_btn = gr.Button("Predict Emotion", variant="primary")

        with gr.Column(scale=1):
            emotion_output = gr.Text(label="Predicted Emotion")
            confidence_output = gr.Text(label="Confidence")
            probs_output = gr.Label(
                label="Emotion Probabilities",
                num_top_classes=4
            )

    submit_btn.click(
        fn=process_file,
        inputs=audio_input,
        outputs=[emotion_output, confidence_output, probs_output]
    )

    gr.Markdown(
        """
        ---
        **Supported formats:** WAV (most compatible) · MP3 · MP4 · MKV · FLAC · OGG · M4A · WEBM (other formats might not be accurate)
        **Model:** MLP Classifier trained on RAVDESS — 4-class emotion recognition  
        **Features:** MFCC · Chroma · Mel Spectrogram · ZCR · RMS · Spectral Contrast · Tonnetz
        """
    )


if __name__ == "__main__":
    interface.launch()