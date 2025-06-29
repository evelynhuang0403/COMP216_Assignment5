import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO
import server
import os

SERVER = "http://127.0.0.1:5000"

class ImageViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter Image Viewer Client") # Title of the GUI window
        self.root.geometry("600x500")
        self.root.resizable(False, False) # Disable resizing
        self.selected_image = tk.StringVar() # Variable to hold the selected image filename
        self.image_list = [] # List to hold available images from the server
        self.tk_image = None  # Placeholder for image reference
        self.setup_ui()
        self.load_image_list()
        print("Tkinter GUI is loading...")  # Debug line

    # Setup the user interface components
    def setup_ui(self):
        # Title Label
        ttk.Label(self.root, text="Select and View Server Images", font=("Arial", 14)).pack(pady=10)
        frame_top = ttk.Frame(self.root)
        frame_top.pack(pady=5, fill='x', padx=10)
        ttk.Label(frame_top, text="Available Images:").grid(row=0, column=0, sticky='w', padx=5)

        # Dropdown for image selection
        self.dropdown = ttk.Combobox(frame_top, textvariable=self.selected_image, state='readonly', width=20)
        self.dropdown.grid(row=0, column=1, padx=5)
        self.dropdown.bind("<<ComboboxSelected>>", self.display_image)

        # Button to upload new image
        ttk.Button(frame_top, text="Upload New Image", command=self.upload_image).grid(row=0, column=2, padx=5)

        # Image Canvas
        self.canvas = tk.Canvas(self.root, width=400, height=300, bg='lightgray')
        self.canvas.pack(pady=0)

        # Metadata Label
        self.meta_label = ttk.Label(self.root, text="Image metadata will appear here.", justify="left")
        self.meta_label.pack(pady=5)

        # Bottom frame for Delete and Exit buttons
        frame_bottom = ttk.Frame(self.root)
        frame_bottom.pack(pady=0, fill='y', padx=0)

        # Button to delete selected image
        ttk.Button(frame_bottom, text="Delete Selected Image", command=self.delete_image).grid(row=0, column=1, padx=10)
        # Exit button to close the application
        ttk.Button(frame_bottom, text="Exit", command=self.root.quit).grid(row=0, column=2, padx=10)

    # Load the list of images from the server and populate the dropdown
    # If images are available, auto-select the first one and display it
    def load_image_list(self):
        try:
            response = requests.get(f"{SERVER}/image-list")
            response.raise_for_status()
            self.image_list = response.json()
            self.dropdown['values'] = self.image_list

            # Auto-select and display first image if available
            if self.image_list:
                self.selected_image.set(self.image_list[0])
                self.display_image()
        except Exception as e:
            messagebox.showerror("Image List Error", f"Could not load images:\n{e}")

    # Display the selected image in the canvas and show its metadata
    # If no image is selected, do nothing
    # If the image fails to load, show an error message
    def display_image(self, event=None):
        filename = self.selected_image.get()
        if not filename:
            return
        try:
            # Get image + metadata
            img_response = requests.get(f"{SERVER}/get-image/{filename}")
            img_response.raise_for_status()
            img_data = Image.open(BytesIO(img_response.content))
            img_data.thumbnail((400, 300))
            self.tk_image = ImageTk.PhotoImage(img_data)
            self.canvas.delete("all")
            self.canvas.create_image(200, 150, image=self.tk_image)

            # Metadata from headers
            headers = img_response.headers
            metadata = (
                f"Filename: {filename}\n"
                f"Format: {headers.get('Image-Format', 'Unknown')}\n"
                f"Size: {headers.get('Image-Size', 'Unknown')}\n"
                f"Mode: {headers.get('Image-Mode', 'Unknown')}"
            )
            self.meta_label.config(text=metadata)
        except Exception as e:
            messagebox.showerror("Image Error", f"Failed to load image:\n{e}")

    # Upload a new image to the server
    # Opens a file dialog to select an image file, then sends it to the server for upload
    # If the upload is successful, refresh the image list
    # If the upload fails, show an error message
    # If no file is selected, do nothing
    def upload_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff")]
        )
        if not file_path:
            return
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                response = requests.post(f"{SERVER}/uploads", files=files)
                response.raise_for_status()
                messagebox.showinfo("Upload Successful", "Image uploaded and converted to PNG.")
                self.load_image_list()
        except Exception as e:
            messagebox.showerror("Upload Error", f"Could not upload image:\n{e}")

    # Delete the selected image from the server
    # If no image is selected, show a warning message
    # If the deletion is confirmed, send a DELETE request to the server
    # If the deletion is successful, refresh the image list
    # If the deletion fails, show an error message
    # If no image is selected, do nothing
    # If the user cancels the deletion, do nothing
    def delete_image(self):
        filename = self.selected_image.get()
        if not filename:
            messagebox.showwarning("No Selection", "Please select an image to delete.")
            return
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {filename}?")
        if not confirm:
            return
        try:
            response = requests.delete(f"{SERVER}/delete-image/{filename}")
            response.raise_for_status()
            messagebox.showinfo("Deleted", f"{filename} has been deleted.")
            self.load_image_list()
        except Exception as e:
            messagebox.showerror("Delete Error", f"Could not delete image:\n{e}")


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
    # Wait for server to be ready before launching GUI
    try:
        wait_for_server_ready()
    except TimeoutError as e:
        print("Error:", e)
        exit(1)
    # Start the GUI
    start_gui()
