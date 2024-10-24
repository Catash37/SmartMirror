from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
import os
import json
import numpy as np
from .forms import RegisterForm
from .utils import load_users, save_user, find_user_by_encoding
import base64
from io import BytesIO
from PIL import Image
from datetime import datetime
import pytz
import cv2  # Import OpenCV
import tensorflow as tf  # Import TensorFlow

main = Blueprint('main', __name__)
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.json')

# Load FaceNet model
model = tf.keras.models.load_model('path_to_facenets_model.h5')  # Update with your model path

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image):
    """Preprocess the image for FaceNet."""
    image = cv2.resize(image, (160, 160))  # Resize to 160x160
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    image = (image / 255.0)  # Normalize to [0, 1]
    return image

def get_face_encoding(image_np):
    """Get face encoding using FaceNet."""
    processed_image = preprocess_image(image_np)
    encoding = model.predict(processed_image)
    return encoding.flatten().tolist()  # Flatten and convert to list for JSON serialization

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        face_image = form.face_image.data
        time_zone = form.time_zone.data
        
        if face_image and allowed_file(face_image.filename):
            filename = secure_filename(face_image.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            face_image.save(file_path)

            # Process face image
            image = cv2.imread(file_path)
            encodings = get_face_encoding(image)
            if encodings:
                encoding = encodings
            else:
                flash('No face detected in the image.', 'danger')
                os.remove(file_path)  # Remove the uploaded file if no face is detected
                return redirect(url_for('main.register'))

            # Save user data locally
            user = {
                'username': username,
                'face_encoding': encoding,
                'image_filename': filename,
                'time_zone': time_zone
            }

            save_user(user)

            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('main.login'))
        else:
            flash('Invalid file type. Only jpg, jpeg, png, and gif are allowed.', 'danger')

    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Expecting base64 image data from the frontend
        data_url = request.form.get('image')
        if not data_url:
            flash('No image data received.', 'danger')
            return redirect(url_for('main.login'))

        # Decode the base64 image
        header, encoded = data_url.split(',', 1)
        data = base64.b64decode(encoded)
        image = Image.open(BytesIO(data)).convert('RGB')
        image_np = np.array(image)

        # Process face image
        encodings = get_face_encoding(image_np)
        if encodings:
            encoding = encodings
        else:
            flash('No face detected in the image.', 'danger')
            return redirect(url_for('main.login'))

        # Find user by encoding
        user = find_user_by_encoding(encoding)
        if user:
            session['username'] = user['username']
            flash(f'Welcome, {user["username"]}!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Face not recognized. Please register or try again.', 'danger')
            return redirect(url_for('main.login'))

    return render_template('login.html')

@main.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('main.login'))
    
    username = session['username']
    user_time_zone = user.get('time_zone', 'UTC')  # Get user's time zone
    timezone = pytz.timezone(user_time_zone)
    current_time = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')  # Current time in user's time zone

    return render_template('dashboard.html', username=username, timezone=user_time_zone, current_time=current_time)

@main.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
