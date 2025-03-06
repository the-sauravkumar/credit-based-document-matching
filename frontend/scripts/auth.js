const API_URL = "http://127.0.0.1:5000";

async function register() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const role = document.getElementById("role").value;  // Get selected role

    const response = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, role })
    });

    const data = await response.json();
    if (response.ok) {
        alert("Registration successful. You can now log in.");
        window.location.href = "login.html";
    } else {
        document.getElementById("error").innerText = data.error;
    }
}


async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();
    if (response.ok) {
        localStorage.setItem("user", JSON.stringify(data));
        alert("Login successful");
        window.location.href = "dashboard.html"; 
    } else {
        document.getElementById("error").innerText = data.error;
    }
}
