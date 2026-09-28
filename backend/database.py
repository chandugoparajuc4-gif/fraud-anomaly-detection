import sqlite3
import os

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "transactions.db"
)


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT,
            amount REAL,
            transaction_hour INTEGER,
            result TEXT,
            anomaly_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def save_transaction(
    transaction_id,
    amount,
    transaction_hour,
    result,
    anomaly_score
):
    connection = get_connection()

    connection.execute("""
        INSERT INTO transactions
        (
            transaction_id,
            amount,
            transaction_hour,
            result,
            anomaly_score
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        transaction_id,
        amount,
        transaction_hour,
        result,
        anomaly_score
    ))

    connection.commit()
    connection.close()


def get_transactions():
    connection = get_connection()

    rows = connection.execute("""
        SELECT
            transaction_id,
            amount,
            transaction_hour,
            result,
            anomaly_score,
            created_at
        FROM transactions
        ORDER BY id DESC
        LIMIT 20
    """).fetchall()

    connection.close()

    return [dict(row) for row in rows]