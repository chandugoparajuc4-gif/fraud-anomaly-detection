
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import pandas as pd

# Project paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")

# Allow Python to find files inside src
sys.path.append(SRC_DIR)

from predict import predict_transaction
from database import create_table, save_transaction, get_transactions

app = Flask(__name__)
CORS(app)

# Create the database table when the app starts
create_table()


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Fraud and Anomaly Detection API is running!"
    })


@app.route("/stats", methods=["GET"])
def stats():
    try:
        dataset_path = os.path.join(
            BASE_DIR, "dataset", "transactions.csv"
        )

        df = pd.read_csv(dataset_path)

        total = len(df)
        suspicious = int(df["is_fraud"].sum())
        normal = total - suspicious

        fraud_rate = (
            round((suspicious / total) * 100, 2)
            if total > 0 else 0
        )

        return jsonify({
            "total_transactions": total,
            "suspicious_transactions": suspicious,
            "normal_transactions": normal,
            "fraud_rate": fraud_rate
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/predict", methods=["POST"])
def predict():
    try:
        transaction = request.get_json()

        if not transaction:
            return jsonify({
                "error": "No transaction data received"
            }), 400

        result, score = predict_transaction(transaction)
        score = round(float(score), 4)

        transaction_id = transaction.get(
            "transaction_id", "WEB_TEST"
        )

        # Save the prediction to SQLite
        save_transaction(
            transaction_id,
            float(transaction["amount"]),
            int(transaction["transaction_hour"]),
            result,
            score
        )

        return jsonify({
            "transaction_id": transaction_id,
            "result": result,
            "anomaly_score": score
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route("/history", methods=["GET"])
def history():
    try:
        transactions = get_transactions()

        return jsonify({
            "transactions": transactions
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )