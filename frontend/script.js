
const API_URL = "http://127.0.0.1:5000";

const form = document.getElementById("transactionForm");
const result = document.getElementById("result");

let transactionChart = null;
let fraudChart = null;

// Check transaction
form.addEventListener("submit", async function (event) {
    event.preventDefault();
    result.textContent = "Checking transaction...";

    const transaction = {
        transaction_id: "WEB_" + Date.now(),
        amount: Number(document.getElementById("amount").value),
        transaction_hour: Number(document.getElementById("hour").value),
        distance_from_home: Number(document.getElementById("distance").value),
        distance_from_last_transaction: Number(document.getElementById("lastDistance").value),
        velocity: Number(document.getElementById("velocity").value),
        device_change: Number(document.getElementById("device").value),
        location_change: Number(document.getElementById("location").value),
        account_age_days: Number(document.getElementById("age").value),
        failed_attempts: Number(document.getElementById("failed").value),
        merchant_category: document.getElementById("category").value
    };

    try {
        const response = await fetch(`${API_URL}/predict`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(transaction)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Request failed");
        }

        addTransactionToHistory(transaction, data);

        const isSuspicious =
            data.result === "SUSPICIOUS TRANSACTION";

        result.innerHTML = `
            <p class="${isSuspicious ? "suspicious" : "normal"}">
                ${data.result}
            </p>
            <p>Anomaly Score: ${data.anomaly_score}</p>
            <small>
                This is an automated anomaly flag, not confirmation
                of fraud. Review the transaction before taking action.
            </small>
        `;

        await loadStatistics();
        await loadTransactionHistory();

    } catch (error) {
        result.textContent = "Error: " + error.message;
    }
});

// Load statistics
async function loadStatistics() {
    try {
        const response = await fetch(`${API_URL}/stats`);

        if (!response.ok) {
            throw new Error("Could not load statistics");
        }

        const stats = await response.json();

        document.getElementById("totalTransactions").textContent =
            Number(stats.total_transactions).toLocaleString();

        document.getElementById("suspiciousTransactions").textContent =
            Number(stats.suspicious_transactions).toLocaleString();

        document.getElementById("normalTransactions").textContent =
            Number(stats.normal_transactions).toLocaleString();

        document.getElementById("fraudRate").textContent =
            stats.fraud_rate + "%";

        createCharts(stats);

    } catch (error) {
        console.error("Statistics error:", error);
    }
}

// Add a transaction to the table
function addTransactionToHistory(transaction, data) {
    const tableBody = document.getElementById("transactionHistory");

    if (!tableBody) return;

    const emptyRow = tableBody.querySelector("td[colspan='5']");
    if (emptyRow) {
        tableBody.innerHTML = "";
    }

    const row = document.createElement("tr");
    const values = [
        transaction.transaction_id,
        `₹${transaction.amount.toFixed(2)}`,
        transaction.transaction_hour,
        data.result,
        data.anomaly_score
    ];

    values.forEach((value, index) => {
        const cell = document.createElement("td");
        cell.textContent = value;

        if (index === 3) {
            cell.className =
                data.result === "SUSPICIOUS TRANSACTION"
                    ? "suspicious-row"
                    : "normal-row";
        }

        row.appendChild(cell);
    });

    tableBody.prepend(row);
}

// Create or update charts
function createCharts(stats) {
    const transactionCanvas =
        document.getElementById("transactionChart");

    const fraudCanvas =
        document.getElementById("fraudChart");

    if (!transactionCanvas || !fraudCanvas) return;

    const normal = Number(stats.normal_transactions);
    const suspicious = Number(stats.suspicious_transactions);

    if (transactionChart) {
        transactionChart.destroy();
    }

    if (fraudChart) {
        fraudChart.destroy();
    }

    transactionChart = new Chart(transactionCanvas, {
        type: "doughnut",
        data: {
            labels: [
                "Normal Transactions",
                "Suspicious Transactions"
            ],
            datasets: [{
                data: [normal, suspicious],
                backgroundColor: ["#3498db", "#ff5b7f"]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: "bottom"
                }
            }
        }
    });

    fraudChart = new Chart(fraudCanvas, {
        type: "bar",
        data: {
            labels: ["Normal", "Suspicious"],
            datasets: [{
                label: "Transactions",
                data: [normal, suspicious],
                backgroundColor: ["#3498db", "#ff5b7f"]
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Load saved transaction history from the backend
async function loadTransactionHistory() {
    const tableBody = document.getElementById("transactionHistory");

    if (!tableBody) return;

    try {
        const response = await fetch(`${API_URL}/history`);

        if (!response.ok) {
            throw new Error("Unable to load transaction history");
        }

        const data = await response.json();
        tableBody.innerHTML = "";

        if (!data.transactions || data.transactions.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5">No transactions checked yet.</td>
                </tr>
            `;
            return;
        }

        data.transactions.forEach(transaction => {
            const row = document.createElement("tr");

            const values = [
                transaction.transaction_id,
                `₹${Number(transaction.amount).toFixed(2)}`,
                transaction.transaction_hour,
                transaction.result,
                transaction.anomaly_score
            ];

            values.forEach((value, index) => {
                const cell = document.createElement("td");
                cell.textContent = value;

                if (index === 3) {
                    cell.className =
                        transaction.result === "SUSPICIOUS TRANSACTION"
                            ? "suspicious-row"
                            : "normal-row";
                }

                row.appendChild(cell);
            });

            tableBody.appendChild(row);
        });

    } catch (error) {
        console.error("History error:", error);
        tableBody.innerHTML = `
            <tr>
                <td colspan="5">Could not load transaction history.</td>
            </tr>
        `;
    }
}

// Load dashboard data when the page opens
loadStatistics();
loadTransactionHistory();



// Download transaction history as CSV
document.getElementById("downloadCsv")
    .addEventListener("click", async function () {
        try {
            const response = await fetch(
                "http://127.0.0.1:5000/history"
            );

            if (!response.ok) {
                throw new Error("Could not fetch transaction history");
            }

            const data = await response.json();
            const transactions = data.transactions || [];

            if (transactions.length === 0) {
                alert("No transactions available to download.");
                return;
            }

            const columns = [
                "transaction_id",
                "amount",
                "transaction_hour",
                "result",
                "anomaly_score",
                "created_at"
            ];

            const escapeCsv = value =>
                '"' + String(value ?? "").replace(/"/g, '""') + '"';

            const rows = [
                columns.join(","),
                ...transactions.map(transaction =>
                    columns.map(column =>
                        escapeCsv(transaction[column])
                    ).join(",")
                )
            ];

            const csv = "\uFEFF" + rows.join("\r\n");
            const blob = new Blob([csv], {
                type: "text/csv;charset=utf-8;"
            });

            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");

            link.href = url;
            link.download = "transaction_history.csv";
            link.click();

            URL.revokeObjectURL(url);
        } catch (error) {
            alert("Download failed: " + error.message);
        }
    });