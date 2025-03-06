import os
import json
import pdfplumber
import pytesseract
from docx import Document
from PIL import Image
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv

upload_bp = Blueprint("upload", __name__)

# Load environment variables
load_dotenv()
TESSERACT_PATH = os.getenv("TESSERACT_PATH", "C:/Program Files/Tesseract-OCR/tesseract.exe")  # Update path for Windows if needed
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Define storage paths
UPLOAD_DIR = "./storage/uploads/"
TEXT_STORAGE_DIR = "./storage/extracted_texts/"

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TEXT_STORAGE_DIR, exist_ok=True)

# Function to extract text from different file types
def extract_text(file_path, file_ext):
    """Extracts text from .txt, .pdf, .docx, and image files."""
    extracted_text = ""

    try:
        if file_ext == "txt":
            with open(file_path, "r", encoding="utf-8") as f:
                extracted_text = f.read()

        elif file_ext == "pdf":
            with pdfplumber.open(file_path) as pdf:
                extracted_text = "\n".join(page.extract_text() or "" for page in pdf.pages)

        elif file_ext == "docx":
            doc = Document(file_path)
            extracted_text = "\n".join(para.text for para in doc.paragraphs)

        elif file_ext in ["jpg", "png"]:
            extracted_text = pytesseract.image_to_string(Image.open(file_path))

        return extracted_text.strip() if extracted_text else None

    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return None

# Route: Handle file uploads
@upload_bp.route("/upload", methods=["POST"])
def upload_file():
    """Handles user file uploads and extracts text."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # Get file extension
    file_ext = file.filename.rsplit(".", 1)[-1].lower()
    allowed_types = {"txt", "pdf", "docx", "jpg", "png"}

    if file_ext not in allowed_types:
        return jsonify({"error": f"Unsupported file type: {file_ext}"}), 400

    # Save file temporarily
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(file_path)

    # Extract text
    extracted_text = extract_text(file_path, file_ext)
    if not extracted_text:
        return jsonify({"error": "Failed to extract text"}), 400

    # Save extracted text to storage
    text_file_path = os.path.join(TEXT_STORAGE_DIR, file.filename + ".txt")
    with open(text_file_path, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    return jsonify({
        "message": "File uploaded successfully",
        "filename": file.filename,
        "text_file": text_file_path,
        "extracted_text": extracted_text[:500]  # Limit text preview
    }), 200
