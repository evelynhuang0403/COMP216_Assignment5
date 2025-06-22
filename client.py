import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO
import server

SERVER = "http://127.0.0.1:5000"


class ImageViewerApp:
    def __init__(self, root):
        #  Before starting the GUI, ensure the server is ready
        wait_for_server_ready()


#  Wait until the server is ready and images are downloaded.
def wait_for_server_ready(timeout=30):
    start_time = time.time()
    while True:
        try:
            response = requests.get(f"{SERVER}/image-list", timeout=2)
            if response.status_code == 200 and response.json():
                print("Server is ready.")
                return True
        except requests.RequestException:
            pass

        if time.time() - start_time > timeout:
            raise TimeoutError("Server did not become ready in time.")

        time.sleep(1)  # Wait a second before retrying


# ---  Run Flask server in background ---
def start_server():
    server.app.run(port=5000, debug=False, use_reloader=False)


# ---  Run GUI client ---
def start_gui():
    root = tk.Tk()
    app = ImageViewerApp(root)
    root.mainloop()


if __name__ == '__main__':
    # Start Flask server in a thread
    flask_thread = threading.Thread(target=start_server, daemon=True)
    flask_thread.start()

    # wait to ensure server is up before GUI makes API calls
    time.sleep(2)

    # Start the GUI
    start_gui()
