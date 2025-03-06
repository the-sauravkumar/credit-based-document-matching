import json
import os
from flask import Blueprint, request, jsonify, session
from routes.admin import update_credit_usage
from apscheduler.schedulers.background import BackgroundScheduler

credits_bp = Blueprint("credits", __name__)

CREDITS_FILE = "./storage/credits.json"
USERS_FILE = "./storage/users.json"
ANALYTICS_FILE = "./storage/analytics.json"

# Ensure storage folder exists
os.makedirs("./storage", exist_ok=True)

# Load users from JSON
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            try:
                data = json.load(f)
                return data if isinstance(data, dict) and "users" in data else {"users": []}
            except json.JSONDecodeError:
                return {"users": []}
    return {"users": []}

# Save users to JSON
def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# Load credit requests
def load_credit_requests():
    if os.path.exists(CREDITS_FILE):
        with open(CREDITS_FILE, "r") as f:
            try:
                data = json.load(f)
                return data if isinstance(data, list) else []
            except json.JSONDecodeError:
                return []
    return []

# Save credit requests
def save_credit_requests(data):
    with open(CREDITS_FILE, "w") as f:
        json.dump(data, f, indent=4)



@credits_bp.route("/credits/request", methods=["POST"])
def request_credits():
    """ Allow users to request more credits. """
    data = request.json
    username = data.get("username")
    requested_credits = data.get("credits")

    if not username or not isinstance(requested_credits, int) or requested_credits <= 0:
        return jsonify({"error": "Invalid request"}), 400

    credit_requests = load_credit_requests()

    # Ensure the user doesn't have a pending request
    if any(req["username"] == username for req in credit_requests):
        return jsonify({"error": "Credit request already pending"}), 400

    credit_requests.append({
        "username": username,
        "credits": requested_credits,
        "status": "pending"
    })
    save_credit_requests(credit_requests)

    return jsonify({"message": "Credit request submitted"}), 200



@credits_bp.route("/credits/approve", methods=["POST"])
def approve_credits():
    """ Admin approves or denies credit requests. """
    data = request.json
    admin_user = data.get("admin")  # Ensure only admins can approve
    username = data.get("username")
    approve = data.get("approve", False)

    users = load_users()
    credit_requests = load_credit_requests()

    # Check if the admin exists and is an admin
    admin_found = next((u for u in users["users"] if u["username"] == admin_user and u["role"] == "admin"), None)
    if not admin_found:
        return jsonify({"error": "Unauthorized"}), 403  # Return 403 only if truly unauthorized

    # Process the request if found
    for req in credit_requests:
        if req["username"] == username:
            user_found = next((u for u in users["users"] if u["username"] == username), None)
            if user_found:
                if approve:
                    user_found["credits"] += req["credits"]
                    save_users(users)
                    message = f"Approved {req['credits']} credits for {username}"
                else:
                    message = f"Denied credit request for {username}"

                # Remove the processed request
                credit_requests = [r for r in credit_requests if r["username"] != username]
                save_credit_requests(credit_requests)

                return jsonify({"message": message}), 200

    return jsonify({"error": "No credit request found"}), 404



@credits_bp.route("/credits/deduct", methods=["POST"])
def deduct_credit():
    """ Deduct 1 credit per scan """
    data = request.json
    username = data.get("username")

    users = load_users()
    user = next((u for u in users["users"] if u["username"] == username), None)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user["credits"] > 0:
        user["credits"] -= 1
        save_users(users)
        
        # Track crdit usage
        update_credit_usage(username, 1)
        
        return jsonify({"message": "Credit deducted"}), 200
    else:
        return jsonify({"error": "Not enough credits"}), 403



@credits_bp.route("/credits/reset", methods=["POST"])
def reset_daily_credits():
    """ Reset daily credits for regular users at midnight """
    print("⏳ Resetting credits at midnight...")
    users = load_users()
    for user in users["users"]:
        if user["role"] == "user":  # Admins retain 9999 credits
            user["credits"] = 20
    save_users(users)
    return jsonify({"message": "Daily credits reset"}), 200

# Schedule the daily credit reset
scheduler = BackgroundScheduler()
scheduler.add_job(reset_daily_credits, "cron", hour=0, minute=0) # Reset daily credits at midnight
scheduler.start()


@credits_bp.route("/admin/credits", methods=["GET"])
def get_credit_requests():
    """ Fetch pending credit requests for the admin panel """
    credit_requests = load_credit_requests()
    return jsonify({"requests": credit_requests if isinstance(credit_requests, list) else []}), 200



@credits_bp.route("/credits/get", methods=["GET"])
def get_credits():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "Username is required"}), 400

    # Example credit lookup (adjust based on your database)
    users = load_users()
    user = next((u for u in users["users"] if u["username"] == username), None)
    user_credits = user["credits"] if user else 0
    
    return jsonify({"credits": user_credits})

