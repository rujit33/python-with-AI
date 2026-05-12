# Real-Time Speech Emotion Recognizer

A machine learning project that classifies the dominant emotion in a speech audio file using acoustic features (MFCCs, Chroma, Mel Spectrogram) and a Multi-Layer Perceptron (MLP) trained on the RAVDESS dataset.

---

## Project Structure

# 📁 Project Structure

```text
SpeechEmotionRecognizer/
│
├── dataset/
│   ├── Actor_01/
│   ├── Actor_02/
│   └── ...
│
|___inference data
|   |__xyz.wav
|
|
├── models/
│   └── emotion_model.pkl
│
├── src/
│   ├── config.py
│   ├── feature_extraction.py
│   ├── data_loader.py
│   ├── train_model.py
│   └── predict.py
│
└── README.md

```

# 📂 Dataset Structure

Audio files are stored in this format:

```
dataset/
├── Actor_01/
│   ├── 03-01-01-01-01-01-01.wav
│   ├── 03-01-06-02-02-02-01.wav
│   └── ...
├── Actor_02/
│   ├── 03-01-06-02-02-02-01.wav
│   ├── 03-01-06-02-02-02-01.wav
│   └── ...
├── Actor_03/
│   └── ...
└── ...
```

---

# 📥 Dataset Source

RAVDESS Emotional Speech Audio Dataset:  
https://www.kaggle.com/datasets/uwrfkaggler/ravdess-emotional-speech-audio?resource=download&select=Actor_24

---

# ⚙️ Core Components

All important components are inside src folder.

## config.py

Central file to manage hyperparameters, dataset paths, and model settings.

---

## data_loader.py

Responsible for:

- Loading audio files
- Extracting labels from filenames
- Splitting dataset into train and test sets

---

## feature_extraction.py

Responsible for:

- Converting raw audio into numerical features
- Extracting MFCC (Mel Frequency Cepstral Coefficients)
- Adding chroma and mel spectrogram features

👉 This step converts audio signals into ML-ready feature vectors.

---

## train_model.py

Responsible for:

- Training the MLPClassifier model
- Evaluating accuracy on test data
- Saving trained model as `.pkl` file

---

## predict.py

Used for inference:

- Loads trained model
- Processes new audio file
- Predicts emotion label

---

## inference data

Contains few sample audio data for testing purpose.
Note that the provided audio samples were not used during training process.

---

# ▶️ How to Run

## Step 1: Open project folder

```powershell
cd "Real-Time Speech Emotion Recognizer"
```

## Step 2: Train model

```
python src/train_model.py
```

## Step 3: Run inference

in the predict.py file replace the file path with the file you wish to predict

```python
if __name__ == "__main__":
    test_audio = <file path>  # Replace with your test audio file path
    predict_emotion(test_audio)
```

and run the following code in your powershell terminal

```powershell
python src/predict.py
```

the output of the inference for a particular file will appear as follows

```
Predicted Emotion : angry
Confidence Score  : 99.96%

All Emotion Probabilities:
angry: 99.96%
happy: 0.04%
neutral: 0.00%
sad: 0.00%
```

## 🎧 Supported Audio Format

👉 .wav only

(MP3 support requires additional preprocessing libraries and is not enabled by default.)

## 💾 Model Output

After training:

Trained model is saved as:
models/emotion_model.pkl

# 🧠 Model Overview

## 🤖 Machine Learning Model Used

This project uses a **Multilayer Perceptron (MLP) Classifier**, which is a type of feedforward artificial neural network provided by Scikit-learn.

👉 Model Used:

- `MLPClassifier` from scikit-learn

## ❗ Important Clarification (No Pretrained Model)

This project does NOT use any pretrained deep learning model.

Instead:

- The model is trained from scratch on the RAVDESS dataset
- It learns patterns directly from extracted audio features (MFCC, Chroma, Mel Spectrogram)

So:

> ✔ This is a custom-trained classical ML model  
> ❌ Not transfer learning

---

## 🧩 How the Model Works

### 1. Input (Audio Signal)

Raw `.wav` audio files are given as input.

---

### 2. Feature Extraction

Audio is converted into numerical feature vectors using:

- MFCC (Mel Frequency Cepstral Coefficients)
- Chroma Features
- Mel Spectrogram

👉 This step converts sound waves → mathematical representation.

---

### 3. Neural Network Processing (MLP)

The extracted feature vector is passed into the MLP classifier:

### Hidden Layer Behavior:

- Learns patterns between voice tone and emotion
- Adjusts internal weights using backpropagation

---

### 4. Output Layer

The final layer predicts one of the emotion classes:

- neutral
- happy
- sad
- angry

---

## ⚙️ Training Process

The model is trained using:

- Supervised learning
- Labeled speech emotion dataset
- Loss minimization (log-loss function)

---
