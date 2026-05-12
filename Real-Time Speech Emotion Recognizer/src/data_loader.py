'''Data loading and preprocessing for speech emotion recognition.'''

import glob
import os
import numpy as np
import librosa

from sklearn.model_selection import train_test_split

from feature_extraction import (
    extract_features,
    _extract_features_from_signal,
    augment_noise,
    augment_time_stretch,
    augment_pitch_shift,
    reduce_noise
)

from config import (
    DATASET_PATH,
    TEST_SIZE,
    RANDOM_STATE,
    EMOTIONS,
    OBSERVED_EMOTIONS
)


def load_dataset():

    features = []
    labels = []

    audio_files = glob.glob(
        os.path.join(
            DATASET_PATH,
            "Actor_*",
            "*.wav"
        )
    )

    if len(audio_files) == 0:
        raise FileNotFoundError(
            "No audio files found in dataset."
        )

    total = len(audio_files)
    processed = 0
    skipped = 0

    print(f"Found {total} audio files. Starting feature extraction...\n")

    for idx, file_path in enumerate(audio_files, 1):

        print(f"\r[{idx}/{total}] Processed: {processed} | Skipped: {skipped}", end="", flush=True)

        try:
            file_name = os.path.basename(file_path)
            emotion_code = file_name.split("-")[2]
            emotion = EMOTIONS.get(emotion_code)

            if emotion not in OBSERVED_EMOTIONS:
                skipped += 1
                continue

            # ── Original sample ──────────────────────────────────────────────
            feature = extract_features(file_path)
            if feature is None:
                skipped += 1
                continue
            features.append(feature)
            labels.append(emotion)
            processed += 1

            # ── Augmented samples ────────────────────────────────────────────
            signal, sr = librosa.load(file_path, sr=None)
            signal = reduce_noise(signal)

            augmented_signals = [
                augment_noise(signal),
                augment_time_stretch(signal, rate=0.9),
                augment_time_stretch(signal, rate=1.1),
                augment_pitch_shift(signal, sr, steps=2),
                augment_pitch_shift(signal, sr, steps=-2),
            ]

            for aug_signal in augmented_signals:
                aug_feature = _extract_features_from_signal(aug_signal, sr)
                if aug_feature is not None:
                    features.append(aug_feature)
                    labels.append(emotion)
                    processed += 1

        except Exception as error:
            skipped += 1
            print(f"\n[WARNING] Skipping {file_path}: {error}")

    print(f"\n\nDone. {processed} files loaded, {skipped} skipped.")

    if len(features) == 0:
        raise ValueError(
            "No valid features extracted. Check your dataset and emotion filters."
        )

    # Cast to float64 — sklearn requires this internally
    features_array = np.array(features, dtype=np.float64)

    # Drop any rows containing NaN or inf
    clean_mask = np.all(np.isfinite(features_array), axis=1)
    dirty_count = np.sum(~clean_mask)

    if dirty_count > 0:
        print(f"[INFO] Dropped {dirty_count} samples with NaN/inf features.")

    features_array = features_array[clean_mask]
    labels = [label for label, keep in zip(labels, clean_mask) if keep]

    if len(features_array) == 0:
        raise ValueError(
            "All features were NaN/inf. Something is wrong with feature extraction."
        )

    return train_test_split(
        features_array,
        labels,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=labels
    )