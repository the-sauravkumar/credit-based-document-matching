from flask import Blueprint, request, jsonify, session
from utils.file_utils import load_json, save_json
import bcrypt

auth_bp = Blueprint("auth", __name__)

# Load users from JSON
def get_users():
    return load_json("users.json").get("users", [])

# Save user data
def save_users(users):
    save_json("users.json", {"users": users})

# Register User
@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "user")  # Default role: user

    users = get_users()
    
    # Check if username exists
    if any(user["username"] == username for user in users):
        return jsonify({"error": "Username already exists"}), 400

    # Hash password
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    # Assign credits based on role
    credits = 9999 if role == "admin" else 20

    # Create user
    new_user = {
        "username": username,
        "password": hashed_pw,
        "role": role,
        "credits": credits  # Assign correct credits
    }

    users.append(new_user)
    save_users(users)

    return jsonify({"message": "User registered successfully"}), 201

# Login User
@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    # users = get_users()
    users = load_json("users.json").get("users", [])
    user = next((u for u in users if u["username"] == username), None)

    if not user or not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode()):
        return jsonify({"error": "Invalid username or password"}), 401

    # Simulated session handling (for local testing)
    session["user"] = {
        "username": user["username"], 
        "role": user["role"], 
        "credits": user["credits"]
    }
    
    session.modified = True # Ensure session is saved or persistence

    return jsonify(
        {"message": "Login successful", 
         "username": user["username"],
         "role": user["role"],
         "credits": user["credits"]
    }), 200

# Logout User
@auth_bp.route("/auth/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"message": "Logged out successfully"}), 200


# Get User Profile
@auth_bp.route("/user/profile", methods=["GET"])
def get_profile():
    print("SESSION DATA AT PROFLE REQUEST:", session.get("user"))  # Debugging Line
    
    user = session.get("user")
    if not user:
        return jsonify({"error": "Not logged in"}), 401
    
    return jsonify(user), 200

# Debug Session
@auth_bp.route("/debug/session", methods=["GET"])
def debug_session():
    session["test"] = "Session is working!"
    return jsonify({"message": "Session stored", "session_data": session.get("test")}), 200

