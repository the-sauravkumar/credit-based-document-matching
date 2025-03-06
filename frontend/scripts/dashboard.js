const API_URL = "http://127.0.0.1:5000";

// Fetch user profile
async function fetchProfile() {
    try {
        const response = await fetch(`${API_URL}/user/profile`, {
            method: "GET",
            credentials: "include"  // Ensures session cookies are sent
        });

        // const data = await response.json();
        if (response.ok) {
            const data = await response.json();
            document.getElementById("username").innerText = data.username;
            document.getElementById("userRole").innerText = data.role;

            // console.log("User Profile Data:", data);
            localStorage.setItem("username", data.username);
            localStorage.setItem("role", data.role);
            localStorage.setItem("credits", data.credits);

           updateCredits(); // Update credits

            fetchScanHistory(data.username); // Fetch scan history

            if (data.role === "admin") {
                document.getElementById("userOptions").style.display = "none";
                document.getElementById("scanDocumentSection").style.display = "none";
                document.getElementById("pastScanSection").style.display = "none";
                document.getElementById("manageCreditsBtn").style.display = "block";
                document.getElementById("viewAnalyticsBtn").style.display = "block";
            }
        } else {
            alert("Session expired. Redirecting to login.");
            window.location.href = "login.html";
        }
    } catch (error) {
        console.error("Failed to fetch profile:", error);
        alert("Server error. Please try again.");
    }
}

// Run when page loads
document.addEventListener("DOMContentLoaded", fetchProfile);


// Fetch Scan History
async function fetchScanHistory(username) {
    try {
        const response = await fetch(`${API_URL}/scan/history?username=${username}`, {
            method: "GET"
        });

        const data = await response.json();
        console.log("Scan History Data:", data);  // Debugging: Check response

        const tableBody = document.getElementById("scanHistory");
        tableBody.innerHTML = ""; // Clear existing content

        if (data.history.length > 0) {
            data.history.forEach(scan => {
                // Correctly access matches inside result
                if (scan.result && scan.result.matches && scan.result.matches.length > 0) {
                    scan.result.matches.forEach(match => {
                        const documentName = match.document_name || "Unknown Document"; 
                        const similarityScore = match.similarity_score || "0%";  
                        // const queryExcerpt = match.document_excerpt || "No query excerpt available.";
                        const insight = match.insight || "No insight available.";

                        const row = document.createElement("tr");
                        row.innerHTML = `
                            <td>${documentName}</td>
                            <td>
                                <strong>Similarity:</strong> ${similarityScore}<br>
                                <strong>Insight:</strong> ${insight}
                            </td>
                        `;
                        tableBody.appendChild(row);
                    });
                } else {
                    tableBody.innerHTML = `<tr><td colspan="2">No matches found.</td></tr>`;
                }
            });
        } else {
            document.getElementById("scan-download-btn").style.display = "none";
            tableBody.innerHTML = `<tr><td colspan="2">No scan history found.</td></tr>`;
        }
    } catch (error) {
        console.error("Error fetching scan history:", error);
    }
}



// Redirect Admins to Credit Management Page
function redirectToAdmin() {
    window.location.href = "admin.html";
}

// Redirects to Upload Module
function redirectToUpload() {
    window.location.href = "upload.html";
}

// Request additional credits (Only for Users)
async function requestCredits() {
    const creditAmount = document.getElementById("creditAmount").value;
    
    if (!creditAmount || creditAmount <= 0) {
        document.getElementById("creditStatus").innerText = "Enter a valid credit amount.";
        return;
    }

    const response = await fetch(`${API_URL}/credits/request`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: localStorage.getItem("username"), credits: parseInt(creditAmount) })
    });

    const data = await response.json();
    document.getElementById("creditStatus").innerText = data.message;
    
}

// Logout function
async function logout() {
    await fetch(`${API_URL}/auth/logout`, { method: "POST", credentials: "include" });
    localStorage.clear();
    window.location.href = "login.html";
}

async function seeAdminAnalytics() {
    window.location.href = "admin_dashboard.html";
}

async function downloadScanHistory() {
    const username = localStorage.getItem("username");
    if (!username) return;

    try {
        const response = await fetch(`${API_URL}/scan/history?username=${username}`);
        const data = await response.json();
        console.log("📜 Preparing Scan History Report:", data);

        let reportContent = `📜 Scan History Report for ${username}\n\n`;
        data.history.forEach(scan => {
            scan.result.matches.forEach(match => {
                reportContent += `📄 Document: ${match.document_name}\n`;
                reportContent += `🔹 Similarity: ${match.similarity_score}\n`;
                reportContent += `📜 Excerpt: ${match.document_excerpt}\n\n`;
                reportContent += `🔍 Insight: ${match.insight}\n\n`;
            });
        });

        // Create and Download Report File
        const blob = new Blob([reportContent], { type: "text/plain" });
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = `${username}_scan_history.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

    } catch (error) {
        console.error("Error downloading report:", error);
    }
}


// Fetch and update credits from backend
async function updateCredits() {
    const username = localStorage.getItem("username");
    const creditsDisplay = document.getElementById("credits");

    if (!username) {
        console.warn("No username found in localStorage.");
        if (creditsDisplay) creditsDisplay.innerText = "Credits: N/A";
        return;
    }

    try {
        console.log(`🔍 Fetching credits for user: ${username}`);
        const response = await fetch(`${API_URL}/credits/get?username=${username}`);

        if (!response.ok) {
            throw new Error(`Failed to fetch credits. HTTP Status: ${response.status}`);
        }

        const data = await response.json();

        if (!data.credits && data.credits !== 0) {
            throw new Error("Invalid response format: 'credits' field missing.");
        }

        localStorage.setItem("credits", data.credits); // Update localStorage
        if (creditsDisplay) creditsDisplay.innerText = `${data.credits}`;

        console.log(`Credits updated successfully: ${data.credits}`);
    } catch (error) {
        console.error("Error fetching credits:", error);
        if (creditsDisplay) creditsDisplay.innerText = "Error";
    }
}