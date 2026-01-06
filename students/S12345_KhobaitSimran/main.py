"""
Iris Flower Classification using Machine Learning
A simple AI project that classifies iris flowers into three species
based on sepal and petal measurements.
"""

import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report


def load_data():
    """Load the Iris dataset."""
    print("Loading Iris dataset...")
    iris = load_iris()
    X = iris.data
    y = iris.target
    target_names = iris.target_names
    feature_names = iris.feature_names
    
    print(f"Dataset loaded successfully!")
    print(f"Number of samples: {len(X)}")
    print(f"Number of features: {len(feature_names)}")
    print(f"Features: {feature_names}")
    print(f"Classes: {list(target_names)}")
    
    return X, y, target_names, feature_names


def preprocess_data(X, y):
    """Split and scale the data."""
    print("\nPreprocessing data...")
    
    # Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")
    
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler


def train_model(X_train, y_train):
    """Train a K-Nearest Neighbors classifier."""
    print("\nTraining KNN classifier...")
    
    model = KNeighborsClassifier(n_neighbors=5)
    model.fit(X_train, y_train)
    
    print("Model trained successfully!")
    return model


def evaluate_model(model, X_test, y_test, target_names):
    """Evaluate the model on test data."""
    print("\n" + "=" * 50)
    print("MODEL EVALUATION")
    print("=" * 50)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy: {accuracy * 100:.2f}%")
    
    # Classification report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=target_names))
    
    return accuracy


def predict_sample(model, scaler, target_names):
    """Make predictions on sample data."""
    print("\n" + "=" * 50)
    print("SAMPLE PREDICTIONS")
    print("=" * 50)
    
    # Sample measurements [sepal_length, sepal_width, petal_length, petal_width]
    samples = [
        [5.1, 3.5, 1.4, 0.2],  # Typical Setosa
        [6.5, 2.8, 4.6, 1.5],  # Typical Versicolor
        [7.2, 3.2, 6.0, 1.8],  # Typical Virginica
    ]
    
    samples_scaled = scaler.transform(samples)
    predictions = model.predict(samples_scaled)
    
    for i, (sample, pred) in enumerate(zip(samples, predictions)):
        print(f"\nSample {i + 1}: {sample}")
        print(f"Predicted class: {target_names[pred]}")


def main():
    """Main function to run the iris classification pipeline."""
    print("=" * 50)
    print("IRIS FLOWER CLASSIFICATION")
    print("AI Project - Machine Learning Demo")
    print("=" * 50)
    
    # Load data
    X, y, target_names, feature_names = load_data()
    
    # Preprocess data
    X_train, X_test, y_train, y_test, scaler = preprocess_data(X, y)
    
    # Train model
    model = train_model(X_train, y_train)
    
    # Evaluate model
    accuracy = evaluate_model(model, X_test, y_test, target_names)
    
    # Make sample predictions
    predict_sample(model, scaler, target_names)
    
    print("\n" + "=" * 50)
    print("PROGRAM COMPLETED SUCCESSFULLY")
    print("=" * 50)
    
    return accuracy


if __name__ == "__main__":
    main()
