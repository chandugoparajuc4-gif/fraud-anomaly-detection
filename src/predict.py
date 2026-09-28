import joblib
import pandas as pd

from features import create_features


def predict_transaction(transaction):
    # Load trained model
    saved_data = joblib.load("models/fraud_model.pkl")

    model = saved_data["model"]
    scaler = saved_data["scaler"]
    columns = saved_data["columns"]

    # Convert transaction into DataFrame
    df = pd.DataFrame([transaction])

    # Create additional features
    df = create_features(df)

    # Remove ID
    df = df.drop(columns=["transaction_id"])

    # Convert merchant category into numeric value
    df["merchant_category"] = (
        df["merchant_category"].astype("category").cat.codes
    )

    # Make sure columns match training columns
    df = df.reindex(columns=columns)

    # Scale data
    df_scaled = scaler.transform(df)

    # Predict
    prediction = model.predict(df_scaled)

    # Get anomaly score
    score = model.decision_function(df_scaled)[0]

    if prediction[0] == -1:
        result = "SUSPICIOUS TRANSACTION"
    else:
        result = "NORMAL TRANSACTION"

    return result, score


if __name__ == "__main__":

    transaction = {
        "transaction_id": "TEST001",
        "amount": 2500.00,
        "transaction_hour": 3,
        "distance_from_home": 1500.00,
        "distance_from_last_transaction": 1200.00,
        "velocity": 8,
        "device_change": 1,
        "location_change": 1,
        "account_age_days": 100,
        "failed_attempts": 4,
        "merchant_category": "online_shopping"
    }

    result, score = predict_transaction(transaction)

    print("\nTransaction Prediction")
    print("----------------------")
    print("Result:", result)
    print("Anomaly Score:", round(score, 4))