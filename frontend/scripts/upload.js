const API_URL = "http://127.0.0.1:5000";

// Fetch and update credits from backend
async function updateCredits() {
    const username = localStorage.getItem("username");
    const creditsDisplay = document.getElementById("creditsDisplay");

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
        if (creditsDisplay) creditsDisplay.innerText = `Credits: ${data.credits}`;

        console.log(`Credits updated successfully: ${data.credits}`);
    } catch (error) {
        console.error("Error fetching credits:", error);
        if (creditsDisplay) creditsDisplay.innerText = "Credits: Error";
    }
}






// Upload and match document
async function uploadAndMatchDocument() {
    const fileInput = document.getElementById("documentUpload");
    const scanStatus = document.getElementById("scanStatus");
    const matchResults = document.getElementById("matchResults");

    if (!fileInput.files.length) {
        scanStatus.innerText = "Please select a file.";
        return;
    }

    const currentCredits = parseInt(localStorage.getItem("credits"));
    if (currentCredits <= 0) {
        scanStatus.innerText = "Not enough credits to scan.";
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);

    try {
        // Upload file
        scanStatus.innerText = "Uploading document...";
        const uploadResponse = await fetch(`${API_URL}/upload`, {
            method: "POST",
            body: formData
        });

        if (!uploadResponse.ok) {
            throw new Error(`Upload failed: ${uploadResponse.status}`);
        }

        const uploadData = await uploadResponse.json();
        scanStatus.innerText = "Document uploaded. Matching now...";
        // Match extracted text using BERT-based AI
        const matchResponse = await fetch(`${API_URL}/scan/match`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: uploadData.extracted_text })
        });

        if (!matchResponse.ok) {
            throw new Error(`Matching failed: ${matchResponse.status}`);
        }

        const matchData = await matchResponse.json();
        // Format results for display
        const matches = matchData.matches || [];

        if (matches.length > 0) {
            let resultText = "<h3>🔍Matched Documents:</h3><br><br>";
            matches.forEach((match, index) => {
                const truncatedDocument = match.document_excerpt
                    ? (match.document_excerpt.length > 100 ? match.document_excerpt.substring(0, 100) + "..." : match.document_excerpt)
                    : "N/A";

                const insight = match.insight || "No additional insights available.";

                resultText += `
                    <div style="border: 1px solid #ccc; padding: 12px; margin: 12px 0; border-radius: 8px; background: #f9f9f9;">
                        <h4>📄 ${index + 1}. <strong>${match.document_name}</strong></h4>
                        <p><strong>🔹 Similarity:</strong> ${match.similarity_score}</p>
                        <p><strong>📜 Document Excerpt:</strong> <br><em>${truncatedDocument}</em></p>
                        <p><strong>💡 Insight:</strong> ${insight}</p>
                    </div>
                `;
            });

            matchResults.innerHTML = resultText;
        } else {
            console.error("No matches found, or API returned incorrect format:", matchData);
            matchResults.innerText = "No significant matches found.";
        }


        // Deduct 1 credit after scanning
        await fetch(`${API_URL}/credits/deduct`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: localStorage.getItem("username") })
        });

        // Fetch updated credits and update UI
        await updateCredits();
    } catch (error) {
        scanStatus.innerText = "Error: " + error.message;
    }
}


// Back to Dashboard
function goBack() {
    window.location.href = "dashboard.html";
}

// Initialize credits on page load
document.addEventListener("DOMContentLoaded", updateCredits);
