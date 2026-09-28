
import os
import numpy as np
import pandas as pd

# Dataset settings
N_ROWS = 50000
SEED = 42
OUTPUT_PATH = "dataset/transactions.csv"

rng = np.random.default_rng(SEED)

# Transaction categories and typical amounts
categories = {
    "grocery": 45,
    "restaurant": 30,
    "fuel": 40,
    "utilities": 80,
    "healthcare": 120,
    "entertainment": 25,
    "clothing": 70,
    "travel": 400,
    "online_shopping": 60,
    "electronics": 350,
    "jewelry": 600,
    "gift_cards": 100
}

names = list(categories.keys())
amounts = np.array(list(categories.values()))

# Choose a merchant category for each transaction
category_index = rng.choice(len(names), size=N_ROWS)
merchant_category = np.array(names)[category_index]

# Generate transaction amounts
amount = amounts[category_index] * rng.lognormal(
    mean=0,
    sigma=0.8,
    size=N_ROWS
)
amount = np.clip(amount, 1, 20000).round(2)

# Generate transaction time
transaction_hour = rng.integers(0, 24, size=N_ROWS)

# Generate distance from home
distance_from_home = rng.exponential(
    scale=6,
    size=N_ROWS
)

far_mask = rng.random(N_ROWS) < 0.06
distance_from_home[far_mask] = rng.uniform(
    100, 3000, size=far_mask.sum()
)
distance_from_home = distance_from_home.round(2)

# Generate device and location changes
device_change = (rng.random(N_ROWS) < 0.08).astype(int)

location_probability = np.where(
    distance_from_home > 100, 0.60, 0.05
)
location_change = (
    rng.random(N_ROWS) < location_probability
).astype(int)

# Generate recent transaction counts
transactions_last_24h = rng.poisson(3, size=N_ROWS)

burst_mask = rng.random(N_ROWS) < 0.04
transactions_last_24h[burst_mask] += rng.integers(
    5, 25, size=burst_mask.sum()
)

transactions_last_1h = rng.binomial(
    transactions_last_24h, 1 / 12
)
transactions_last_1h[burst_mask] = np.minimum(
    transactions_last_24h[burst_mask],
    rng.integers(3, 15, size=burst_mask.sum())
)

# Generate account age and failed attempts
account_age_days = np.clip(
    rng.exponential(900, size=N_ROWS).astype(int) + 1,
    1,
    5000
)

failed_attempts = np.minimum(
    rng.poisson(0.15, size=N_ROWS),
    5
)

# Create a synthetic risk score
is_night = (transaction_hour <= 5).astype(int)
is_far = (distance_from_home > 100).astype(int)
is_new_account = (account_age_days < 60).astype(int)

risk_score = (
    1.1 * is_night
    + 1.2 * is_far
    + 0.3 * np.log1p(distance_from_home)
    + device_change
    + 0.9 * location_change
    + 0.35 * transactions_last_1h
    + 0.08 * transactions_last_24h
    + 1.1 * is_new_account
    + 0.7 * failed_attempts
    + rng.normal(0, 0.8, size=N_ROWS)
)

# Convert risk score into fraud probability
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

low, high = -30, 5

for _ in range(60):
    mid = (low + high) / 2
    if sigmoid(risk_score + mid).mean() > 0.03:
        high = mid
    else:
        low = mid

intercept = (low + high) / 2
fraud_probability = sigmoid(risk_score + intercept)

is_fraud = (
    rng.random(N_ROWS) < fraud_probability
).astype(int)

# Build the dataset
df = pd.DataFrame({
    "transaction_id": [
        f"TXN{i:08d}" for i in range(1, N_ROWS + 1)
    ],
    "amount": amount,
    "transaction_hour": transaction_hour,
    "distance_from_home": distance_from_home,
    "device_change": device_change,
    "location_change": location_change,
    "transactions_last_1h": transactions_last_1h,
    "transactions_last_24h": transactions_last_24h,
    "account_age_days": account_age_days,
    "failed_attempts": failed_attempts,
    "merchant_category": merchant_category,
    "is_fraud": is_fraud
})

# Shuffle the records
df = df.sample(
    frac=1,
    random_state=SEED
).reset_index(drop=True)

# Save the dataset
os.makedirs("dataset", exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False)

# Display a summary
print(f"Saved {len(df):,} transactions to {OUTPUT_PATH}")
print(df.head())
print(f"\nFraud count: {df['is_fraud'].sum():,}")
print(f"Fraud rate: {df['is_fraud'].mean():.2%}")