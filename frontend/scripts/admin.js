const API_URL = "http://127.0.0.1:5000";

// Fetch credit requests and display them
async function fetchCreditRequests() {
    try {
        console.log("Fetching credit requests...");
        const response = await fetch(`${API_URL}/admin/credits`, {
            method: "GET",
            credentials: "include",
            headers: { "Content-Type": "application/json" }
        });

        console.log("Response status:", response.status);

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Credit Requests Data:", data);

        displayCreditRequests(data.requests); // Callling function to update UI
    } catch (error) {
        console.error("Error fetching credit requests:", error);
    }
}


// Function to display credit requests in the admin panel
function displayCreditRequests(requests) {
    const requestTable = document.getElementById("creditRequestsTable");
    requestTable.innerHTML = "";

    if (!requests || requests.length === 0) {
        requestTable.innerHTML = "<tr><td colspan='3'>No pending credit requests</td></tr>";
        return;
    }

    requests.forEach((request) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${request.username}</td>
            <td>${request.credits}</td>
            <td>
                <button onclick="approveCredits('${request.username}')">Approve</button>
                <button onclick="denyCredits('${request.username}')">Deny</button>
            </td>
        `;
        requestTable.appendChild(row);
    });
}

// Function to approve a credit request
async function approveCredits(username) {
    try {
        const response = await fetch(`${API_URL}/credits/approve`, {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ admin: localStorage.getItem("username"), username: username, approve: true })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Approval Response:", data);
        alert(data.message);
        fetchCreditRequests(); // Refresh the list after approval
    } catch (error) {
        console.error("Error approving request:", error);
    }
}

// Function to deny a credit request
async function denyCredits(username) {
    try {
        const response = await fetch(`${API_URL}/credits/approve`, {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ admin: localStorage.getItem("username"), username: username, approve: false })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Denial Response:", data);
        alert(data.message);
        fetchCreditRequests(); // Refresh the list after denial
    } catch (error) {
        console.error("Error denying request:", error);
    }
}

async function backToDashboard() {
    window.location.href = "dashboard.html";
}
// Run when page loads
document.addEventListener("DOMContentLoaded", fetchCreditRequests);
