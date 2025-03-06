### **How to Use the `Test File` for Document Matching**  

The project uses a **document matching system** where uploaded documents are compared against **reference documents** stored in the backend. To test the system effectively, follow these steps:

---

### **1️ Understanding Reference Documents & Test File**
-  **Reference Documents**: Located in `backend/storage/reference_docs`. These are the **source documents** used for matching.
-  **Test File**: A manually created collection of files that serve as **test cases** for document matching.  
-  The files in the **Test File** folder may be **similar to** or **different from** the reference documents. However, for higher similarity scores, they should contain **overlapping or related content**.

---

### **2️ How to Add a New Test File for Matching**
If you want to **test a new document**, follow these steps:

1. **Ensure the document exists in the reference folder** (`backend/storage/reference_docs`):
   - If the document you are testing is missing from `reference_docs`, **you can still upload and match it**.
   - However, if you want **higher similarity scores**, add relevant documents (with similar or overlapping topics) to `reference_docs`.

2. **Upload the document via the web interface**:
   - Navigate to the **Upload & Match** page.
   - Select a file from the **Test File** folder or any other document.
   - Click **"Upload & Match"**.

3. **View the Matching Results**:
   - The system will compare the uploaded document with the reference documents.
   - Matching is based on **text extraction and word similarity**.
   - **Note**: Even if the uploaded document is different from those in `reference_docs`, it may still get a match based on extracted text, but the similarity score may be lower.

---

### **3️ Example Use Case**
🔹 **Scenario**: You have a document named **"invoice_123.pdf"** in the Test File.  
🔹 **Steps**:
   1. **Ensure** `backend/storage/reference_docs/invoice_123.pdf` exists if you want a high similarity match.
   2. **Upload** `invoice_123.pdf` (or any other file) from the Test File folder.
   3. **Check** the matching results.

 **Important**:  
- If `invoice_123.pdf` **does not exist** in `reference_docs`, the system **can still attempt matching** based on text similarity with other stored documents.  
- However, **higher similarity scores** occur when the reference documents contain **related content**.

---

### **4️ Important Notes**
- **Matching is based on extracted text**: The system works by analyzing words and text structure, so it may still return matches even if the uploaded file is not in `reference_docs`.  
- **No Exact Match Needed**: Users can upload **any file**—it does not have to be in `reference_docs`.  
- **Higher Similarity Requires Relevant Documents**: If you want **higher similarity scores**, add **relevant** or **overlapping** documents to `reference_docs`.  
- **Supported File Formats**: `.txt`, `.docx`, `.pdf`, `.jpg`, `.png`.

Now you are ready to **test and verify document matching results** using the Test File! 🚀