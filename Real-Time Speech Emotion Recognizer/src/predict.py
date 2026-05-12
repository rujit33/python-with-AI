import os
import pickle
import numpy as np
from feature_extraction import extract_features
from config import MODEL_PATH, SCALER_PATH, EMOTIONS

def predict_emotion(audio_path):

    try:

        with open(MODEL_PATH, "rb") as model_file:
            model = pickle.load(model_file)

        with open(SCALER_PATH, "rb") as scaler_file:
            scaler = pickle.load(scaler_file)

        features = extract_features(audio_path)

        if features is None:
            print("[ERROR] Feature extraction returned None.")
            return None

        # Match exact dtype and shape used during training
        features = np.array(features, dtype=np.float64)

        if not np.all(np.isfinite(features)):
            print("[ERROR] Features contain NaN or inf values.")
            return None
        features = np.expand_dims(features, axis=0)

        # Apply same scaler used during training
        features = scaler.transform(features)

        
        # prediction = model.predict(features)
        # predicted_emotion = prediction[0]
        # print(f"Predicted : {predicted_emotion}")
        # return predicted_emotion

        #! Get probabilities for all emotions
        probabilities = model.predict_proba(features)[0]    

        #! Get index of highest probability
        predicted_index = np.argmax(probabilities)
        #! Get predicted label
        predicted_emotion = model.classes_[predicted_index]
        #! Confidence score
        confidence = probabilities[predicted_index] * 100
        print(f"Predicted Emotion : {predicted_emotion}")
        print(f"Confidence Score  : {confidence:.2f}%")
        #! Print all emotion probabilities
        print("\nAll Emotion Probabilities:")
        for emotion, probability in zip(model.classes_, probabilities):
            print(f"{emotion}: {probability * 100:.2f}%")
        return predicted_emotion


    except FileNotFoundError as error:
        print(f"[ERROR] File not found: {error}")
        return None
    except Exception as error:
        print(f"[ERROR] Prediction failed: {error}")
        return None


if __name__ == "__main__":
    test_audio = r"E:\internship\Real-Time Speech Emotion Recognizer\inference data\anger1.wav"  # Replace with your test audio file path
    predict_emotion(test_audio)