from datetime import datetime
from flask import Blueprint, request, jsonify, session
import os
import json
import pdfplumber
import pytesseract
import mimetypes
import fitz
from PIL import Image
from docx import Document
import numpy as np
from dotenv import load_dotenv
import torch
import faiss
from sentence_transformers import SentenceTransformer, util
from routes.admin import update_scan_analytics

match_bp = Blueprint("match", __name__)

# Constants
ACTIVITY_LOG_FILE = "./storage/activity_logs.json"

# Load environment variables
load_dotenv()


# Load Model (Moves to GPU if Available)
device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer("BAAI/bge-large-en-v1.5").to(device)

# Define FAISS index
embedding_dim = model.get_sentence_embedding_dimension()
index = faiss.IndexFlatL2(embedding_dim)  # L2 distance (Euclidean)

# Store document metadata
doc_names = []
doc_texts = []


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file using pdfplumber and PyMuPDF."""
    text = ""

    # Try pdfplumber first
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    except Exception as e:
        print(f"WARNING: pdfplumber failed for {pdf_path}, trying PyMuPDF... ({e})")

    # If pdfplumber fails, try PyMuPDF
    if not text:
        try:
            doc = fitz.open(pdf_path)
            text = "\n".join([page.get_text("text") for page in doc])
        except Exception as e:
            print(f"ERROR: Failed to extract text from {pdf_path} using PyMuPDF! ({e})")

    return text.strip()

# Extract text from a plain text file
def extract_text_from_txt(txt_path):
    """Extract text from a plain text file."""
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        print(f"ERROR: Failed to read text file {txt_path}! ({e})")
        return ""

# Extract text from a Word document (.docx)
def extract_text_from_docx(docx_path):
    """Extract text from a Word document (.docx)."""
    try:
        doc = Document(docx_path)
        return "\n".join([para.text for para in doc.paragraphs]).strip()
    except Exception as e:
        print(f"ERROR: Failed to extract text from {docx_path}! ({e})")
        return ""

# Extract text from an image using Tesseract OCR
def extract_text_from_image(img_path):
    """Extract text from an image using Tesseract OCR."""
    try:
        img = Image.open(img_path)
        return pytesseract.image_to_string(img).strip()
    except Exception as e:
        print(f"ERROR: Failed to extract text from {img_path}! ({e})")
        return ""

# Load stored reference documents
def load_reference_docs():
    """Load and store reference document embeddings in FAISS."""
    global index, doc_names, doc_texts

    storage_dir = "./storage/reference_docs"
    docs = {}
    
    if not os.path.exists(storage_dir):
        print(f"ERROR: Reference documents folder {storage_dir} not found!")
        return {}

    for filename in os.listdir(storage_dir):
        file_path = os.path.join(storage_dir, filename)
        mime_type, _ = mimetypes.guess_type(file_path) # Get MIME type
        text = ""
        if mime_type:
            if mime_type == "application/pdf":
                text = extract_text_from_pdf(file_path)
            elif mime_type == "text/plain":
                text = extract_text_from_txt(file_path)
            elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text = extract_text_from_docx(file_path)
            elif mime_type.startswith("image/"):
                text = extract_text_from_image(file_path)
        else:
            print(f"WARNING: Unknown file type for {filename}, skipping...")
        
        if text:
            docs[filename] = text
            print(f"Extracted text from {filename}!")
        else:
            print(f"ERROR: Failed to extract text from {filename}!")
    if not docs:
        print("ERROR: No reference documents loaded!")
        return {}
    
    doc_names = list(docs.keys())
    doc_texts = list(docs.values())
    
    print(f"Generating embeddings for {len(doc_texts)} documents...")
    doc_embeddings = model.encode(doc_texts, convert_to_tensor=False)
    index.add(np.array(doc_embeddings))
    
    print(f"SUCCESS: Loaded {len(doc_texts)} documents into FAISS")
    return docs


#  Match Query Text Against Reference Documents
def match_with_faiss(query_text, top_k=3):
    if not doc_names:
        print("DEBUG: No reference documents loaded!")  # Debug log
        return {"matches": [], "error": "No reference documents available."}

    query_embedding = model.encode(query_text, convert_to_tensor=False).reshape(1, -1)
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for i, idx in enumerate(indices[0]):
        similarity_score = (1 - distances[0][i]) * 100

        if similarity_score < 2:
            continue  # Skip low-matching results

        results.append({
            "document_name": doc_names[idx],
            "similarity_score": f"{similarity_score:.2f}%",
            "document_excerpt": doc_texts[idx][:200] + "..." if len(doc_texts[idx]) > 200 else doc_texts[idx],
            "insight": f"The document '{doc_names[idx]}' is {similarity_score:.2f}% similar to the query text."
        })

    if not results:
        print(f"DEBUG: No significant matches for '{query_text}'")  # Debug log

    return {"matches": results}







import uuid
def store_match_result(username, result):
    """Save match results in a dictionary for future reference."""
    storage_file = "./storage/scans.json"

    # Ensure file exists with an empty dictionary if not present
    if not os.path.exists(storage_file):
        with open(storage_file, "w") as f:
            json.dump({}, f)

    # Load existing scan results
    with open(storage_file, "r") as f:
        try:
            scans = json.load(f)  # Expecting a dictionary
        except json.JSONDecodeError:
            scans = {}  # Reset if JSON file is corrupted
    
    # Generate a unique key (UUID) for each entry
    scan_id = str(uuid.uuid4())
    scans[scan_id] = {
        "username": username,
        "result": result
    }
    
    # Save back to the file
    with open(storage_file, "w") as f:
        json.dump(scans, f, indent=4)




def get_stored_match_results(username):
    """Fetch stored match results for a given user."""
    storage_file = "./storage/scans.json"

    try:
        with open(storage_file, "r") as file:
            scans = json.load(file)

        # Filter entries that match the username
        user_matches = [
            entry["result"].get("matches", [])
            for entry in scans.values()
            if entry.get("username") == username
        ]

        # Flatten list of lists (if multiple scans exist)
        return [match for sublist in user_matches for match in sublist]

    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Ensure storage directory and activity log file exist
def ensure_storage():
    """Ensure that the storage directory and activity log file exist."""
    os.makedirs("./storage", exist_ok=True)  # Ensure the storage folder exists
    if not os.path.exists(ACTIVITY_LOG_FILE):  # Ensure the log file exists
        with open(ACTIVITY_LOG_FILE, "w") as f:
            json.dump([], f, indent=4)  # Initialize as an empty JSON array

def load_json(filepath):
    """Loads a JSON file and returns its content."""
    ensure_storage()  # Ensure directory and file exist before opening

    with open(filepath, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []  # Return empty list if file is corrupted

def save_json(filepath, data):
    """Saves data to a JSON file."""
    ensure_storage()  # Ensure directory and file exist before saving

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def log_user_activity(username, action, details=""):
    """Log user actions like scans and credit requests."""
    logs = load_json(ACTIVITY_LOG_FILE)

    logs.append({
        "username": username,
        "action": action,
        "details": details,
        "timestamp": datetime.now().isoformat()
    })

    save_json(ACTIVITY_LOG_FILE, logs)  # Save updated logs



# Route: Match extracted text with stored documents
@match_bp.route("/scan/match", methods=["POST"])
def match_text():
    """Matches extracted text against stored reference documents."""
    data = request.json
    query_text = data.get("text", "").strip()

    user_data = session.get("user")
    if not user_data:
        return jsonify({"error": "User not logged in"}), 401
    
    username = user_data.get("username", "guest_user")

    if not query_text:
        return jsonify({"error": "No text provided"}), 400

     # Ensure FAISS has reference documents loaded before matching
    if index.ntotal == 0:
        print("DEBUG: FAISS index is empty! Reloading reference documents...")
        load_reference_docs()
    
    # reference_docs = load_reference_docs()
    result = match_with_faiss(query_text, top_k=2)
    
    # Extract document name from the first match (if exists)
    best_match = result.get("matches", [{}])[0]
    document_name = best_match.get("document_name", "Unknown Document")
    
    # Update Analytics
    update_scan_analytics(username, query_text, document_name)
    
    # Log a document scan
    log_user_activity(username, "Scanned Document", document_name)  
    
    store_match_result(username, result)
    stored_results = get_stored_match_results(username)

    return jsonify({"matches": stored_results})



@match_bp.route("/scan/history", methods=["GET"])
def get_scan_history():
    """Fetch past scan history for the logged-in user."""
    username = request.args.get("username", "")

    if not username:
        return jsonify({"error": "Username is required"}), 400

    storage_file = "./storage/scans.json"
    if not os.path.exists(storage_file):
        return jsonify({"history": []})

    with open(storage_file, "r") as f:
        scans = json.load(f)

    user_scans = []
    for scan_id, scan_data in scans.items():
        if scan_data.get("username") == username:
            matches = scan_data.get("result", {}).get("matches", [])
            
            # Extract document name from the first match (if exists)
            document_name = matches[0].get("document_name", "Unknown Document") if matches else "Unknown Document"
            
            user_scans.append({
                "id": scan_id,
                "document_name": document_name,  # Use extracted document_name
                "result": scan_data.get("result", "No match found")
            })

    return jsonify({"history": user_scans})

