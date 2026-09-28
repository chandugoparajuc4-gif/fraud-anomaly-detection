import os
import joblib
import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix

from features import create_features

# Load dataset
df = pd.read_csv("dataset/transactions.csv")

# Create additional features
df = create_features(df)

# Separate labels from input features
y = df["is_fraud"]
X = df.drop(columns=["is_fraud", "transaction_id"])

# Convert category names into numbers
X["merchant_category"] = (
    X["merchant_category"].astype("category").cat.codes
)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train anomaly detection model
model = IsolationForest(
    n_estimators=100,
    contamination=0.03,
    random_state=42
)

model.fit(X_train_scaled)

# Predict anomalies: -1 means anomaly, 1 means normal
predictions = model.predict(X_test_scaled)

# Convert predictions to 0 = normal, 1 = suspicious
y_pred = (predictions == -1).astype(int)

# Evaluate against synthetic labels
print("Model training completed!")
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(
    y_test, y_pred, zero_division=0
))

# Save model and scaler
os.makedirs("models", exist_ok=True)

joblib.dump(
    {
        "model": model,
        "scaler": scaler,
        "columns": list(X.columns)
    },
    "models/fraud_model.pkl"
)

print("\nModel saved to models/fraud_model.pkl")