# Iris Flower Classification

## Project Description

This project implements a machine learning model to classify iris flowers into three species:
- **Setosa**
- **Versicolor**
- **Virginica**

The classification is based on four measurements:
- Sepal length
- Sepal width
- Petal length
- Petal width

The project uses the K-Nearest Neighbors (KNN) algorithm from scikit-learn to perform the classification.

## How to Run

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the main program:
```bash
python main.py
```

## Expected Output

The program will:
1. Load the Iris dataset (150 samples)
2. Split data into training (80%) and testing (20%) sets
3. Train a KNN classifier
4. Display model accuracy and classification report
5. Make predictions on sample flower measurements

**Sample output:**
```
==================================================
IRIS FLOWER CLASSIFICATION
AI Project - Machine Learning Demo
==================================================
Loading Iris dataset...
Dataset loaded successfully!
Number of samples: 150
Number of features: 4

Accuracy: 100.00%

Classification Report:
              precision    recall  f1-score   support

      setosa       1.00      1.00      1.00        10
  versicolor       1.00      1.00      1.00        10
   virginica       1.00      1.00      1.00        10
```

## Author

- **Student ID:** S12345
- **Name:** Khobait Simran
