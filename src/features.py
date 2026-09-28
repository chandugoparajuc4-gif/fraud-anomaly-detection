import pandas as pd

def create_features(df):
    df = df.copy()

    df["is_night"] = (
        (df["transaction_hour"] >= 0) &
        (df["transaction_hour"] < 6)
    ).astype(int)

    df["is_high_amount"] = (
        df["amount"] > df["amount"].quantile(0.95)
    ).astype(int)

    df["is_far_from_home"] = (
        df["distance_from_home"] > 100
    ).astype(int)

    df["failed_attempts_flag"] = (
        df["failed_attempts"] >= 3
    ).astype(int)

    return df


if __name__ == "__main__":
    df = pd.read_csv("dataset/transactions.csv")
    df = create_features(df)

    print("Feature engineering completed!")
    print("Dataset shape:", df.shape)
    print("New features:")
    print([
        "is_night",
        "is_high_amount",
        "is_far_from_home",
        "failed_attempts_flag"
    ])
    print(df.head())