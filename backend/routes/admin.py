import os
import json
from flask import Blueprint, request, jsonify, session
from utils.file_utils import load_json, save_json
from sklearn.feature_extraction.text import TfidfVectorizer
import re

admin_bp = Blueprint("admin", __name__)

CREDITS_FILE = "./storage/credits.json"
USERS_FILE = "./storage/users.json"
ANALYTICS_FILE = "./storage/analytics.json"
ACTIVITY_LOG_FILE = "./storage/activity_logs.json"

# Function to extract top keywords from a list of texts
def extract_top_keywords(all_texts, top_n=10):
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    feature_names = vectorizer.get_feature_names_out()
    tfidf_sum = tfidf_matrix.sum(axis=0)

    keywords_scores = [(feature_names[i], tfidf_sum[0, i]) for i in range(len(feature_names))]
    sorted_keywords = sorted(keywords_scores, key=lambda x: x[1], reverse=True)

    return [word for word, _ in sorted_keywords[:top_n]]

# Load analytics data
def load_analytics():
    if not os.path.exists(ANALYTICS_FILE) or os.stat(ANALYTICS_FILE).st_size == 0:
        print("Analytics file is missing or empty. Initializing with default structure.")
        return {"scans_per_user": {}}  # Ensure default structure

    with open(ANALYTICS_FILE, "r", encoding="utf-8") as f:
        try:
            analytics = json.load(f)
            # Ensure 'scans_per_user' exists
            if "scans_per_user" not in analytics:
                analytics["scans_per_user"] = {}
            if "most_scanned_documents" not in analytics:
                analytics["most_scanned_documents"] = {}
            if "credit_usage" not in analytics:
                analytics["credit_usage"] = {}
            if "most_scanned_topics" not in analytics:
                analytics["most_scanned_topics"] = []
            if "document_texts" not in analytics:
                analytics["document_texts"] = {}
                
            return analytics
        except json.JSONDecodeError:
            return {
                "scans_per_user": {},
                "most_scanned_documents": {},
                "credit_usage": {}
            }  # Return default structure

# Save analytics data
def save_analytics(data):
    with open(ANALYTICS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Update Analytics after Scan
def update_scan_analytics(username, query_text, document_name):
    analytics = load_analytics()

    # Ensure 'scans_per_user' exists
    if "scans_per_user" not in analytics:
        analytics["scans_per_user"] = {}
        
    # Ensure 'most_scanned_documents' exists    
    if "most_scanned_documents" not in analytics:
        analytics["most_scanned_documents"] = {}
    
    # Ensure 'credit_usage' exists
    if "credit_usage" not in analytics:
        analytics["credit_usage"] = {}
        
    if "most_scanned_topics" not in analytics:
        analytics["most_scanned_topics"] = []

    if "document_texts" not in analytics:
        analytics["document_texts"] = {}

    # Now update safely
    analytics["scans_per_user"][username] = analytics["scans_per_user"].get(username, 0) + 1
    
    # Track Most Scanned Documents
    analytics["most_scanned_documents"][document_name] = analytics["most_scanned_documents"].get(document_name, 0) + 1
    
    # Track Document Texts
    analytics["document_texts"][document_name] = query_text
    # Extract Top Keywords
    all_texts = list(analytics["document_texts"].values())
    analytics["most_scanned_topics"] = extract_top_keywords(all_texts)
    

    # Write back safely
    with open(ANALYTICS_FILE, "w", encoding="utf-8") as f:
        json.dump(analytics, f, indent=4)


# Update Credit Usage
def update_credit_usage(username, credit_used):
    analytics = load_analytics()
    
    # Ensure 'credit_usage' exists
    if "credit_usage" not in analytics:
        analytics["credit_usage"] = {}
        
    # Track Credit Usage
    analytics["credit_usage"][username] = analytics["credit_usage"].get(username, 0) + credit_used
    
    # Write back safely
    with open(ANALYTICS_FILE, "w", encoding="utf-8") as f:
        json.dump(analytics, f, indent=4)


# API: Get Analytics for Admin Panel
@admin_bp.route("/admin/analytics", methods=["GET"])
def get_admin_analytics():
    analytics = load_analytics()
    return jsonify(analytics)


# Approve credit request
@admin_bp.route("/admin/approve_credit", methods=["POST"])
def approve_credit():
    data = request.json
    username = data.get("username")
    credits_to_add = data.get("credits")

    users = load_json(USERS_FILE)
    credit_requests = load_json(CREDITS_FILE)

    # Find user
    for user in users:
        if user["username"] == username:
            user["credits"] += credits_to_add
            save_json(USERS_FILE, users)
            break
    else:
        return jsonify({"error": "User not found"}), 404

    # Remove approved request
    credit_requests = [req for req in credit_requests if req["username"] != username]
    save_json(CREDITS_FILE, credit_requests)

    return jsonify({"message": f"Approved {credits_to_add} credits for {username}"}), 200



# Deny credit request
@admin_bp.route("/admin/deny_credit", methods=["POST"])
def deny_credit():
    data = request.json
    username = data.get("username")

    credit_requests = load_json(CREDITS_FILE)

    # Remove denied request
    updated_requests = [req for req in credit_requests if req["username"] != username]
    
    if len(updated_requests) == len(credit_requests):
        return jsonify({"error": "Request not found"}), 404

    save_json(CREDITS_FILE, updated_requests)
    return jsonify({"message": f"Denied credit request for {username}"}), 200


def load_credit_requests():
    """Load credit requests from JSON."""
    if not os.path.exists(CREDITS_FILE):
        return {}
    with open(CREDITS_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}  # Prevents crashes if JSON is corrupted



@admin_bp.route("/admin/credits", methods=["GET"])
def get_credit_requests():
    """Return all pending credit requests (Admin Only)."""
    # Ensure the user is logged in
    user = session.get("user")
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    # Ensure only admins can access
    if user["role"] != "admin":
        return jsonify({"error": "Forbidden"}), 403

    # Load and return credit requests
    credit_requests = load_credit_requests()
    return jsonify(credit_requests), 200


@admin_bp.route("/admin/logs", methods=["GET"])
def get_user_logs():
    return jsonify(load_json(ACTIVITY_LOG_FILE))
