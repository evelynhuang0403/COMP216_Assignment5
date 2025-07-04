# COMP216 - Image Server and Client

This project implements a Flask-based image server for COMP216 Assignment 5 – Part A.  
It provides endpoints for image download, listing, metadata retrieval, upload, and deletion.  
The server also converts all uploaded images to PNG format.

---

### Features:
- Downloads 12 JPG images from Unsplash and converts them to PNG.
- Exposes RESTful endpoints to:
  - List all PNG images (`/image-list`)
  - Get an image with metadata (`/get-image/<filename>`)
  - Upload an image and auto-convert to PNG (`/uploads`)
  - Delete an image (`/delete-image/<filename>`) (Bonus)
 
### 🔧 Install Required Dependencies

Run the following commands in your terminal to install the required Python libraries:

```bash
pip install flask
pip install pillow
pip install requests
```

### 📄 File: `server.py`

The server will:

- Automatically download and convert 12 JPG images from Unsplash into PNG format.

- Start a local Flask server at: http://127.0.0.1:5000

### 📄 File: `client.py`

This script:
- Starts the Flask server from `server.py`
- Waits until image download & conversion is done
- Launches a GUI to interact with the server
