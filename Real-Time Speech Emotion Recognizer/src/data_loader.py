import glob
import os
import numpy as np

from sklearn.model_selection import train_test_split

from feature_extraction import extract_features

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

            feature = extract_features(file_path)

            if feature is None:
                skipped += 1
                continue

            features.append(feature)
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

    # Drop any rows containing NaN or inf — these crash sklearn's early stopping
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
