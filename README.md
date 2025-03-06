# Credit Based Document Matching

## Overview
This project is a **self-contained document scanning and matching system** with a built-in **credit system**. Each user has **20 free scans per day**, and additional scans require admin-approved credits. The system supports **AI-powered document matching** using **FAISS and BERT embeddings**.

### Features:
**User Management & Authentication** (Regular Users & Admins)  
**Credit System** (20 free scans/day, admin approval for extra credits)  
**Document Scanning & Matching** (Basic & AI-based matching using FAISS & BERT)  
**Admin Dashboard** (Scans per user, most scanned topics, credit usage statistics)  
**Multi-user Support** (Session-based authentication)  
**Activity Logs** (Track user actions)  
**Automated Credit Reset** (Daily reset at midnight)  
**Export Reports** (Download scan history as a text file)  

## Tech Stack
### Frontend:
- HTML, CSS, JavaScript (No frameworks)

### Backend:
- **Python (Flask)**
- **Flask Session** for authentication
- **SentenceTransformers (BERT-based embeddings)**
- **FAISS (Efficient similarity search)**
- **TF-IDF for basic text matching**
- **Flask-CORS** for handling requests across frontend & backend
- **Flask-APScheduler** for automated credit resets

### Storage:
- JSON-based storage (users, documents, credits, scan history)
- Local file system for storing reference documents & extracted text

## Installation
### Prerequisites:
- Python 3.8+
- pip installed
- NVIDIA GPU (Optional for faster processing)

### Setup:
```bash
# Clone the repository
git clone https://github.com/the-sauravkumar/credit-based-document-matching.git
cd credit-based-document-matching

# Install dependencies
pip install -r requirements.txt

# Change the directory
cd backend

# Then run the Flask app
python app.py
```

## Usage
### 1. User Authentication
- **Register** a new user via `/auth/register`
- **Login** via `/auth/login` (Session-based authentication)
- **Admins** have additional permissions to approve credit requests & view analytics

### 2. Credit System
- **Every user gets 20 free scans per day** (auto-reset at midnight)
- **Users can request more credits** via `/credits/request`
- **Admins can approve/deny requests** via `/credits/approve`
- **Each document scan deducts 1 credit**

### 3. Document Upload & AI-Based Matching
- **Upload a document** via `/upload`
- **Extract text & match against stored references**
- **FAISS & BERT embeddings for semantic search**
- **Returns top-matching documents with similarity scores**

### 4. Admin Dashboard
- View **scans per user**
- Track **most scanned documents**
- Analyze **credit usage per user**
- Approve/Deny credit requests

## API Endpoints
| Method | Endpoint | Description |
|--------|---------|-------------|
| **POST** | `/auth/register` | User registration |
| **POST** | `/auth/login` | User login (Session-based) |
| **GET** | `/user/profile` | Get user profile & credits |
| **POST** | `/scan/match` | Upload document for scanning (uses 1 credit) |
| **GET** | `/scan/history` | Get user's past scans |
| **POST** | `/credits/request` | Request admin to add credits |
| **POST** | `/credits/approve` | Admin approves/denies credit requests |
| **GET** | `/admin/analytics` | Get analytics for admin |

## Security & Performance
- **Secure password hashing** (bcrypt)
- **Session-based authentication** with JWT enhancement
- **Multi-user support** (Simultaneous logins handled correctly)
- **Optimized search with FAISS** (Scales for large datasets)

## Contribution
Feel free to fork the repo, submit issues, and create pull requests! 🚀

## License
This project is licensed under the MIT License.

