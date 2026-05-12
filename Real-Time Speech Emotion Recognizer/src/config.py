"""
Central configuration file
"""

# =========================
# DATASET CONFIGURATION
# =========================
DATASET_PATH = r"E:\internship\Real-Time Speech Emotion Recognizer\datasets"
TEST_SIZE = 0.2
RANDOM_STATE = 42


# =========================
# AUDIO CONFIGURATION
# =========================
SUPPORTED_FORMATS = [".wav", ".mp3"]
N_MFCC = 60


# =========================
# MODEL CONFIGURATION
# =========================
HIDDEN_LAYER_SIZES = (512, 256, 128)
ACTIVATION = "relu"
LEARNING_RATE = "adaptive"
BATCH_SIZE = 256
MAX_ITERATIONS = 1000
ALPHA = 0.001
EARLY_STOPPING = False
VALIDATION_FRACTION = 0.1


# =========================
# MODEL PATH
# =========================
MODEL_PATH = r"E:\internship\Real-Time Speech Emotion Recognizer\models\emotion_model.pkl"
SCALER_PATH = r"E:\internship\Real-Time Speech Emotion Recognizer\models\scaler.pkl"


# =========================
# EMOTION LABELS
# =========================
EMOTIONS = {
    '01': 'neutral',
    '02': 'calm',
    '03': 'happy',
    '04': 'sad',
    '05': 'angry',
    '06': 'fearful',
    '07': 'disgust',
    '08': 'surprised'
}


OBSERVED_EMOTIONS = [
    'neutral',
    'happy',
    'sad',
    'angry'
]