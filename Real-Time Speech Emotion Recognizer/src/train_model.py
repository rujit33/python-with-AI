import os
import pickle
import numpy as np
from sklearn.metrics import accuracy_score, classification_report
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

from data_loader import load_dataset

from config import (
    HIDDEN_LAYER_SIZES,
    LEARNING_RATE,
    BATCH_SIZE,
    MAX_ITERATIONS,
    ALPHA,
    RANDOM_STATE,
    EARLY_STOPPING,
    VALIDATION_FRACTION,
    MODEL_PATH,
    SCALER_PATH
)


def train():

    print("Loading dataset...")

    x_train, x_test, y_train, y_test = load_dataset()

    print(f"Train samples: {len(x_train)} | Test samples: {len(x_test)}")

    

    # Scale features — critical for MLP, do NOT skip this
    scaler = StandardScaler()
    x_train = scaler.fit_transform(x_train)
    x_test = scaler.transform(x_test)

    print("\nTraining model...")

    model = MLPClassifier(
        hidden_layer_sizes=HIDDEN_LAYER_SIZES,
        learning_rate=LEARNING_RATE,
        batch_size=BATCH_SIZE,
        max_iter=MAX_ITERATIONS,
        alpha=ALPHA,
        random_state=RANDOM_STATE,
        early_stopping=EARLY_STOPPING,
        validation_fraction=VALIDATION_FRACTION,
        verbose=True
    )

    model.fit(x_train, y_train)

    predictions = model.predict(x_test)

    accuracy = accuracy_score(y_test, predictions)

    print(f"\nAccuracy: {accuracy * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, predictions))

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    with open(MODEL_PATH, "wb") as model_file:
        pickle.dump(model, model_file)

    with open(SCALER_PATH, "wb") as scaler_file:
        pickle.dump(scaler, scaler_file)

    print("Model and scaler saved successfully.")


if __name__ == "__main__":
    train()