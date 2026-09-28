# Fraud and Anomaly Detection System

## Project Overview
The Fraud and Anomaly Detection System is a machine learning-based web application that analyzes financial transactions and flags potentially suspicious activity.

## Features
- Transaction fraud and anomaly prediction
- Anomaly score display
- Transaction history
- Dashboard statistics
- Transaction distribution charts
- CSV export of transaction history
- Flask REST API
- Interactive web dashboard

## Technologies Used
- Python
- Pandas and NumPy
- Scikit-learn
- Flask
- HTML, CSS, and JavaScript
- Chart.js
- SQLite (if configured)

## Project Structure
- backend/ - Flask API
- frontend/ - Web dashboard
- dataset/ - Transaction dataset
- models/ - Trained machine learning models
- src/ - Data generation, preprocessing, training, and prediction

## How to Run
1. Open the project folder in VS Code.
2. Activate the Python virtual environment.
3. Install dependencies using: pip install -r requirements.txt
4. Start the backend using: python backend/app.py
5. Open frontend/index.html using VS Code Live Server.
6. Enter transaction details and click Check Transaction.

## Dataset
The project uses synthetic transaction data for development and testing. The generated labels are not real-world fraud confirmations.

## Limitations
The model may produce false positives or miss suspicious transactions. Predictions should be reviewed and must not be treated as proof of fraud.

## Future Enhancements
- Add user authentication
- Add downloadable reports
- Improve model evaluation
- Deploy the application to a web server

## Conclusion
This project demonstrates how machine learning, Flask, and web technologies can be combined to build an interactive transaction anomaly detection system.