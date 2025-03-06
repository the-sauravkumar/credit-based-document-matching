# import json
# import os

# STORAGE_PATH = "./storage"

# def load_json(filename):
#     """Load JSON data from a file."""
#     filepath = os.path.join(STORAGE_PATH, filename)
#     if not os.path.exists(filepath):
#         with open(filepath, "w") as f:
#             json.dump({}, f)
#     with open(filepath, "r") as f:
#         return json.load(f)

# def save_json(filename, data):
#     """Save JSON data to a file."""
#     filepath = os.path.join(STORAGE_PATH, filename)
#     with open(filepath, "w") as f:
#         json.dump(data, f, indent=4)

import json
import os

STORAGE_PATH = "./storage"

def load_json(filename):
    """Load JSON data from a file, ensuring proper structure for users.json."""
    filepath = os.path.join(STORAGE_PATH, filename)
    
    # Ensure the storage folder exists
    os.makedirs(STORAGE_PATH, exist_ok=True)
    
    # If the file doesn't exist, create it with a proper default structure
    if not os.path.exists(filepath):
        default_data = {"users": []} if filename == "users.json" else {}
        with open(filepath, "w") as f:
            json.dump(default_data, f, indent=4)

    # Load the file content
    with open(filepath, "r") as f:
        try:
            data = json.load(f)
            # Ensure that users.json always has a "users" key
            if filename == "users.json" and not isinstance(data, dict):
                return {"users": data if isinstance(data, list) else []}
            return data
        except json.JSONDecodeError:
            return {"users": []} if filename == "users.json" else {}

def save_json(filename, data):
    """Save JSON data to a file."""
    filepath = os.path.join(STORAGE_PATH, filename)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)
