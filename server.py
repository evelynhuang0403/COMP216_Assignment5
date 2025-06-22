# server.py

import os
import requests
from flask import Flask, jsonify, request, Response
from PIL import Image

app = Flask(__name__)
UPLOAD_FOLDER = 'images'

# Images from Assignment 5 - Part I
img_urls = [
    'https://images.unsplash.com/photo-1504208434309-cb69f4fe52b0',
    'https://images.unsplash.com/photo-1485833077593-4278bba3f11f',
    'https://images.unsplash.com/photo-1593179357196-ea11a2e7c119',
    'https://images.unsplash.com/photo-1526515579900-98518e7862cc',
    'https://images.unsplash.com/photo-1582376432754-b63cc6a9b8c3',
    'https://images.unsplash.com/photo-1567608198472-6796ad9466a2',
    'https://images.unsplash.com/photo-1487213802982-74d73802997c',
    'https://images.unsplash.com/photo-1552762578-220c07490ea1',
    'https://images.unsplash.com/photo-1569691105751-88df003de7a4',
    'https://images.unsplash.com/photo-1590691566903-692bf5ca7493',
    'https://images.unsplash.com/photo-1497206365907-f5e630693df0',
    'https://images.unsplash.com/photo-1469765904976-5f3afbf59dfb'
]

# Create the /images directory to store the Part I images
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Function to download images and convert them to PNG (Part A - 1.a, 1.b)
def download_and_convert_images():
    for i, url in enumerate(img_urls):
        try:
            # Define paths for the downloaded JPG and converted PNG images
            jpg_path = os.path.join(UPLOAD_FOLDER, f'image_{i + 1}.jpg')
            png_path = os.path.join(UPLOAD_FOLDER, f'image_{i + 1}.png')

            # Check if the PNG already exists, if not, download and convert
            if not os.path.exists(png_path):
                download_image(url, jpg_path)  # Download the image from the URL
                convert_image_png(jpg_path)  # Convert the downloaded image to PNG
                os.remove(jpg_path)  # Clean up .jpg after conversion
        except Exception as e:
            print(f"Failed to process image {i + 1}: {e}")


# GET method to retrieve a list of available (All) PNG images (/image-list) (Part A - 1.c)
@app.route('/image-list', methods=['GET'])
def image_list():
    try:
        all_files = os.listdir(UPLOAD_FOLDER)  # List all files in the images directory

        # Filter and return only PNG files
        png_files = [filename for filename in all_files if filename.lower().endswith('.png')]

        # Return the list as a JSON response
        return jsonify(png_files)
    except Exception as e:
        return jsonify({'error': f'Failed to list images: {str(e)}'}), 500


# GET method to retrieve a specific image by filename and its related properties
# (/get-image/<filename>) (Part A - 1.d)
@app.route('/get-image/<filename>', methods=['GET'])
def get_image(filename):
    try:
        path = os.path.join(UPLOAD_FOLDER, filename)

        # if the file does not exist, return a 404 error
        if not os.path.isfile(path):
            return jsonify({'error': 'File not found'}), 404

        # Open image and extract properties
        image = Image.open(path)
        image_format = image.format
        image_size = f"{image.size[0]}x{image.size[1]}"
        image_mode = image.mode

        # Read image bytes
        with open(path, 'rb') as f:
            image_data = f.read()

        # Return image as binary, with metadata in custom headers
        response = Response(image_data, mimetype='image/png')
        response.headers['Image-Format'] = image_format
        response.headers['Image-Size'] = image_size
        response.headers['Image-Mode'] = image_mode

        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# POST method to upload a new image to the server and convert to PNG
# (/uploads) Part A.1.e and A.1.f
@app.route('/uploads', methods=['POST'])
def upload_image():
    try:
        # Check if file part is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        # Validate filename
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        # Save the uploaded file to a temporary location
        original_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(original_path)

        # Open and convert to PNG
        image = Image.open(original_path)
        png_filename = os.path.splitext(file.filename)[0] + '.png'
        png_path = os.path.join(UPLOAD_FOLDER, png_filename)
        image.save(png_path, 'PNG')

        # Clean up original (non-PNG) file
        if original_path != png_path:
            os.remove(original_path)

        # Image list is updated automatically since it's just based on the /images folder (Part A.1.f)
        return jsonify({'message': f"{file.filename} uploaded and converted to {png_filename}."})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# DELETE method to delete an image by filename
# (/delete-image/<filename>) (Extra Credit)
@app.route('/delete-image/<filename>', methods=['DELETE'])
def delete_image(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    # Check if the file exists
    if os.path.exists(path):
        os.remove(path) # delete the file from the server
        return jsonify({'message': f'{filename} deleted successfully.'}), 200
    else:
        return jsonify({'error': 'File not found.'}), 404


# Helper functions for downloading and converting images
def download_image(url, output_path):
    try:
        response = requests.get(url)  # Make a HTTP GET request to fetch a response object with an image
        with open(output_path, 'wb') as image_file:  # Capture the image data in binary format as a local file
            image_file.write(response.content)
        return output_path  # Return the path of the saved image
    except Exception as e:
        print(f"Download error for {url}: {e}")
        return None


def convert_image_png(input_path):
    try:
        image = Image.open(input_path)  # Use Pillow (PIL) to open image file object
        png_path = os.path.splitext(input_path)[0] + '.png'  # Change the file extension to .png
        image.save(png_path, 'PNG')  # Save the image in PNG format
        return png_path
    except Exception as e:
        print(f"Conversion error for {input_path}: {e}")
        return None


if __name__ == '__main__':
    download_and_convert_images()
    app.run(port=5000, debug=True)
