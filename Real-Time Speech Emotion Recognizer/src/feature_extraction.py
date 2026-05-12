import librosa
import numpy as np
import os

from config import (
    SUPPORTED_FORMATS,
    N_MFCC
)


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


def extract_features(file_path):

    try:
        validate_audio_file(file_path)

        signal, sample_rate = librosa.load(
            file_path,
            sr=None
        )

        if len(signal) == 0:
            raise ValueError(
                "Audio file is empty."
            )

        signal = reduce_noise(signal)

        result = np.array([])

        stft = np.abs(
            librosa.stft(signal)
        )

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

        # Tonnetz — called directly on signal, no harmonic separation
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

        print(
            f"\n[ERROR] Feature extraction failed for {file_path}: {error}"
        )

        return None