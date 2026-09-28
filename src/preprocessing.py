import pandas as pd
from sklearn.preprocessing import StandardScaler

def load_data(path="dataset/transactions.csv"):
    df = pd.read_csv(path)
    return df

def preprocess_data(df):
    df = df.copy()

    df = df.drop(columns=["transaction_id"])

    df["merchant_category"] = (
        df["merchant_category"].astype("category").cat.codes
    )

    y = df["is_fraud"]
    X = df.drop(columns=["is_fraud"])

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_scaled = pd.DataFrame(
        X_scaled,
        columns=X.columns
    )

    return X_scaled, y, scaler

if __name__ == "__main__":
    df = load_data()
    X, y, scaler = preprocess_data(df)

    print("Data loaded successfully!")
    print("Features:", X.shape)
    print("Fraud labels:", y.shape)
    print("Preprocessing completed!")