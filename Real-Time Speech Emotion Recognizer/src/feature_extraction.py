'''Feature extraction module for speech emotion recognition.'''

import librosa
import numpy as np
import os

from config import (
    SUPPORTED_FORMATS,
    N_MFCC
)


# =========================
# AUGMENTATION HELPERS
# =========================

def augment_noise(signal, noise_factor=0.005):
    noise = np.random.randn(len(signal))
    return signal + noise_factor * noise


def augment_time_stretch(signal, rate=0.9):
    return librosa.effects.time_stretch(signal, rate=rate)


def augment_pitch_shift(signal, sample_rate, steps=2):
    return librosa.effects.pitch_shift(signal, sr=sample_rate, n_steps=steps)


# =========================
# VALIDATION & PREPROCESSING
# =========================

def validate_audio_file(file_path):

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    extension = os.path.splitext(file_path)[1].lower()

    if extension not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )


def reduce_noise(audio):

    max_value = np.max(np.abs(audio))

    if max_value > 0:
        audio = audio / max_value

    return audio


# =========================
# CORE FEATURE EXTRACTION
# =========================

def _extract_features_from_signal(signal, sample_rate):
    """
    Extracts features directly from a pre-loaded signal array.
    Used for augmented samples so we don't re-read from disk.
    """
    try:
        if len(signal) == 0:
            return None

        result = np.array([])

        stft = np.abs(librosa.stft(signal))

        # MFCC Features
        mfccs = np.mean(
            librosa.feature.mfcc(
                y=signal,
                sr=sample_rate,
                n_mfcc=N_MFCC
            ).T,
            axis=0
        )
        result = np.hstack((result, mfccs))

        # Chroma Features
        chroma = np.mean(
            librosa.feature.chroma_stft(
                S=stft,
                sr=sample_rate
            ).T,
            axis=0
        )
        result = np.hstack((result, chroma))

        # Mel Spectrogram
        mel = np.mean(
            librosa.feature.melspectrogram(
                y=signal,
                sr=sample_rate
            ).T,
            axis=0
        )
        result = np.hstack((result, mel))

        # Zero Crossing Rate
        zcr = np.mean(
            librosa.feature.zero_crossing_rate(
                y=signal
            ).T,
            axis=0
        )
        result = np.hstack((result, zcr))

        # RMS Energy
        rms = np.mean(
            librosa.feature.rms(
                y=signal
            ).T,
            axis=0
        )
        result = np.hstack((result, rms))

        # Spectral Contrast
        spectral_contrast = np.mean(
            librosa.feature.spectral_contrast(
                S=stft,
                sr=sample_rate
            ).T,
            axis=0
        )
        result = np.hstack((result, spectral_contrast))

        # Tonnetz
        tonnetz = np.mean(
            librosa.feature.tonnetz(
                y=signal,
                sr=sample_rate
            ).T,
            axis=0
        )
        result = np.hstack((result, tonnetz))

        return result

    except Exception as error:
        print(f"\n[ERROR] Augmented feature extraction failed: {error}")
        return None


def extract_features(file_path):
    """
    Loads audio from disk, validates it, then extracts features.
    """
    try:
        validate_audio_file(file_path)

        signal, sample_rate = librosa.load(
            file_path,
            sr=None
        )

        if len(signal) == 0:
            raise ValueError("Audio file is empty.")

        signal = reduce_noise(signal)

        return _extract_features_from_signal(signal, sample_rate)

    except Exception as error:
        print(f"\n[ERROR] Feature extraction failed for {file_path}: {error}")
        return None