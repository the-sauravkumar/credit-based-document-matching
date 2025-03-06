const API_URL = "http://127.0.0.1:5000";

// Fetch Admin Analytics Data
async function fetchAdminAnalytics() {
    try {
        const response = await fetch(`${API_URL}/admin/analytics`, { method: "GET" });
        const data = await response.json();
        console.log("📊 Admin Analytics Data:", data);

        // Update Scans Per User Table
        const scansTable = document.getElementById("scansPerUser");
        scansTable.innerHTML = "";
        for (const [user, scans] of Object.entries(data.scans_per_user)) {
            scansTable.innerHTML += `<tr><td>${user}</td><td>${scans}</td></tr>`;
        }

        // Update Top Scanned Documents Table
        const documentsTable = document.getElementById("mostScannedDocuments");
        documentsTable.innerHTML = "";
        for (const [topic, count] of Object.entries(data.most_scanned_documents)) {
            documentsTable.innerHTML += `<tr><td>${topic}</td><td>${count}</td></tr>`;
        }
        
        // Update Top Scanned Topics Table
        const topicsTable = document.getElementById("topScannedTopics");
        topicsTable.innerHTML = "";
        if (Array.isArray(data.most_scanned_topics)) {
            data.most_scanned_topics.forEach(topic => {
                topicsTable.innerHTML += `<tr><td>${topic}</td></tr>`;
            });
        }

        // Update Credit Usage Table
        const creditsTable = document.getElementById("creditUsage");
        creditsTable.innerHTML = "";
        for (const [user, credits] of Object.entries(data.credit_usage)) {
            creditsTable.innerHTML += `<tr><td>${user}</td><td>${credits}</td></tr>`;
        }
    } catch (error) {
        console.error("Error fetching analytics data:", error);
    }
}

// Run on Page Load
document.addEventListener("DOMContentLoaded", fetchAdminAnalytics);
