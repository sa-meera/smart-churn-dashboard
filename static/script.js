let pieChartInstance = null;

async function loadDashboard() {

    // Fetch summary data
    const response = await fetch("/risk-summary");
    const data = await response.json();

    document.getElementById("totalCustomers").innerText = data.total;
    document.getElementById("highRiskCustomers").innerText = data.high_risk;

    // Destroy old chart if exists (prevents duplication on refresh)
    if (pieChartInstance) {
        pieChartInstance.destroy();
    }

    const ctx = document.getElementById("churnPieChart").getContext("2d");

    pieChartInstance = new Chart(ctx, {
        type: "pie",
        data: {
            labels: ["High Risk", "Medium Risk", "Low Risk"],
            datasets: [{
                data: [
                    data.high_risk,
                    data.medium_risk,
                    data.low_risk
                ],
                backgroundColor: [
                    "#ef4444",
                    "#facc15",
                    "#22c55e"
                ]
            }]
        },
        options: {
            responsive: true
        }
    });

    loadHighRiskTable();
}

async function loadHighRiskTable() {
    const response = await fetch("/high-risk");
    const customers = await response.json();

    const table = document.getElementById("highRiskTable");
    table.innerHTML = "";

    customers.forEach(customer => {
        const row = `
            <tr>
                <td>${customer.CustomerId}</td>
                <td>${customer.Age}</td>
                <td>${customer.Geography}</td>
                <td>${customer.Balance}</td>
                <td>${(customer.churn_probability * 100).toFixed(2)}%</td>
            </tr>
        `;
        table.innerHTML += row;
    });
}

// Initial load
loadDashboard();

// Auto-refresh every 10 seconds
setInterval(loadDashboard, 10000);