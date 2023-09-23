from flask import Flask, flash, request, redirect, url_for, render_template
import os
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
import cv2

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Preprocess and resize the uploaded image
        processed_image = preprocess_image(file_path)

        # Perform OCR on the preprocessed image
        ocr_text = extract_text_from_image(processed_image)

        flash('Image successfully uploaded and displayed below')
        return render_template('index.html', filename=filename, ocr_text=ocr_text)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

def preprocess_image(image_path):
    try:
        # Read the image using cv2
        image = cv2.imread(image_path)

        # Resize the image to a reasonable size for OCR
        resized_image = cv2.resize(image, (800, 600))

        # Convert to grayscale
        gray_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

        # Save the preprocessed image and return its path
        processed_path = os.path.join(app.config['UPLOAD_FOLDER'], 'processed_' + os.path.basename(image_path))
        cv2.imwrite(processed_path, gray_image)

        return processed_path
    except Exception as e:
        print(f"Error during image preprocessing: {str(e)}")
        return image_path

def extract_text_from_image(image_path):
    try:
        # Open the preprocessed image using PIL
        image = Image.open(image_path)

        # Perform OCR using pytesseract
        ocr_text = pytesseract.image_to_string(image, lang='eng')  # Replace 'eng' with appropriate language code if needed

        return ocr_text
    except Exception as e:
        print(f"Error during OCR: {str(e)}")
        return "Error during OCR"

if __name__ == "__main__":
    app.run()
