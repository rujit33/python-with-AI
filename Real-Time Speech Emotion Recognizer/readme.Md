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

The following line of code extracts the True value of file.

```python
emotion_code = file_name.split("-")[2]
```

for example for the following audio file in training dataset

```
03-01-05-01-02-01-12.wav
```

Python creates a list:

```python
[
    "03",
    "01",
    "05",
    "01",
    "02",
    "01",
    "12.wav"
]
```

Now indexing starts from 0.

```
Index	Value
0	"03"
1	"01"
2	"05"
3	"01"
4	"02"
5	"01"
6	"12.wav"

```

So:

```python
file_name.split("-")[2]
```

means:

```python
"05"
```

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

## utils.py

Provides a function to convert audio file formats to .wav format for Compatibility.

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

## 💾 Model Output

After training:

Trained model is saved as:
models/emotion_model.pkl

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

## Results

```powershell
(.env) PS E:\internship\Real-Time Speech Emotion Recognizer> python src/train_model.py
Loading dataset...
Found 1440 audio files. Starting feature extraction...

[1440/1440] Processed: 4032 | Skipped: 767

Done. 4032 files loaded, 768 skipped.
Train samples: 3225 | Test samples: 807

Training model...
Iteration 1, loss = 1.11221759
Iteration 2, loss = 0.70951072
Iteration 3, loss = 0.48274498
Iteration 4, loss = 0.33966359
Iteration 5, loss = 0.22445688
Iteration 6, loss = 0.16004759
Iteration 7, loss = 0.11518596
Iteration 8, loss = 0.07048944
Iteration 9, loss = 0.04887767
Iteration 10, loss = 0.03653616
Iteration 11, loss = 0.02267206
Iteration 12, loss = 0.01477620
Iteration 13, loss = 0.01062252
Iteration 14, loss = 0.00818739
Iteration 15, loss = 0.00646214
Iteration 16, loss = 0.00547121
Iteration 17, loss = 0.00473377
Iteration 18, loss = 0.00423886
Iteration 19, loss = 0.00384319
Iteration 20, loss = 0.00360729
Iteration 21, loss = 0.00341168
Iteration 22, loss = 0.00323025
Iteration 23, loss = 0.00310701
Iteration 24, loss = 0.00301564
Iteration 25, loss = 0.00287930
Iteration 26, loss = 0.00279959
Iteration 27, loss = 0.00271712
Iteration 28, loss = 0.00265892
Iteration 29, loss = 0.00260596
Iteration 30, loss = 0.00255344
Iteration 31, loss = 0.00249798
Iteration 32, loss = 0.00245921
Iteration 33, loss = 0.00242447
Iteration 34, loss = 0.00239036
Iteration 35, loss = 0.00236840
Iteration 36, loss = 0.00233547
Training loss did not improve more than tol=0.000100 for 10 consecutive epochs. Stopping.

Accuracy: 88.60%

Classification Report:
              precision    recall  f1-score   support

       angry       0.92      0.91      0.91       230
       happy       0.89      0.91      0.90       231
     neutral       0.81      0.83      0.82       115
         sad       0.89      0.86      0.87       231

    accuracy                           0.89       807
   macro avg       0.88      0.88      0.88       807
weighted avg       0.89      0.89      0.89       807

Model and scaler saved successfully.
```

---

## app.py (Inference Via Gradio)

An interface was provided to the ML model using Gradio.

Run the following command inorder start the application.

(working directory should be "Real-Time Speech Emotion Recognizer" folder )

```powershell
python src/app.py
```
