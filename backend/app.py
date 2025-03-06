import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_session import Session
from routes.auth import auth_bp
from routes.credits import credits_bp
from routes.admin import admin_bp
from routes.match import match_bp
from routes.upload import upload_bp

# Ensure Flask finds frontend files
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Get backend folder path
FRONTEND_FOLDER = os.path.join(BASE_DIR, "../frontend")  # Adjust for your folder structure

app = Flask(__name__, static_folder=FRONTEND_FOLDER, static_url_path="")

# Ensure session storage directory exists
SESSION_DIR = os.path.join(BASE_DIR, "flask_session")
if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)

# Configure Flask Session
app.config["SESSION_TYPE"] = "filesystem" # Store session data in the filesystem
app.config["SESSION_PERMANENT"] = False # Make the session data transient
app.config["SESSION_USE_SIGNER"] = True # Sign session data
app.config["SESSION_FILE_DIR"] = SESSION_DIR  # Use the ensured directory
app.config["SECRET_KEY"] = "supersecretkey" # Secret key for signing

Session(app)

# Enable CORS (Allow Frontend Requests)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

# Serve the frontend root (index.html)
@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

# Serve any static file (HTML, CSS, JS)
@app.route("/<path:filename>")
def serve_static_files(filename):
    return send_from_directory(app.static_folder, filename)

# Register Routes (API Endpoints)
app.register_blueprint(auth_bp)
app.register_blueprint(credits_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(match_bp)
app.register_blueprint(upload_bp)

if __name__ == "__main__":
    app.run(debug=True)
