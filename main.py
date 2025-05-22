from flask import Flask, render_template, request, flash, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import cv2
import os
import numpy as np

app = Flask(__name__)
app.secret_key = "your-secret-key-here"  # Change this to a secure secret key
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS 

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'webp', 'png', 'jpg', 'jpeg', 'gif'}

def processImage(filename, format_conversion=None, image_processing=None):
    print(f"Format Conversion: {format_conversion}, Image Processing: {image_processing}, Filename: {filename}")
    img = cv2.imread(f"uploads/{filename}")



    # Handle format conversions
    if format_conversion:
        match format_conversion:
            case "cwebp":
                newFilename = f"static/{filename.split('.')[0]}.webp"
                cv2.imwrite(newFilename, img)
                return newFilename
            case "cpng":
                newFilename = f"static/{filename.split('.')[0]}.png"
                cv2.imwrite(newFilename, img)
                return newFilename
            case "cjpg":
                newFilename = f"static/{filename.split('.')[0]}.jpg"
                cv2.imwrite(newFilename, img)
                return newFilename
            case "cjpeg":
                newFilename = f"static/{filename.split('.')[0]}.jpeg"
                cv2.imwrite(newFilename, img)
                return newFilename

    # Handle image processing
    if image_processing:
        match image_processing:
            case "cgray":
                imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                newFilename = f"static/{filename}"
                cv2.imwrite(newFilename, imgProcessed)
                return newFilename
            case "histeq":
                imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                imgProcessed = cv2.equalizeHist(imgGray)
                newFilename = f"static/{filename.split('.')[0]}_histeq.png"
                cv2.imwrite(newFilename, imgProcessed)
                return newFilename
            case "blur":
                imgProcessed = cv2.GaussianBlur(img, (5, 5), 0)
                newFilename = f"static/{filename.split('.')[0]}_blurred.png"
                cv2.imwrite(newFilename, imgProcessed)
                return newFilename
            case "canny":
                imgProcessed = cv2.Canny(img, 100, 200)
                newFilename = f"static/{filename.split('.')[0]}_edges.png"
                cv2.imwrite(newFilename, imgProcessed)
                return newFilename
            case "rotate":
                imgProcessed = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                newFilename = f"static/{filename.split('.')[0]}_rotated.png"
                cv2.imwrite(newFilename, imgProcessed)
                return newFilename
            case "sharpen":
                kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
                imgProcessed = cv2.filter2D(img, -1, kernel)
                newFilename = f"static/{filename.split('.')[0]}_sharpened.png"
                cv2.imwrite(newFilename, imgProcessed)
                return newFilename
            
 #add new features , add under the image_processing
          
            case "crop":
                # Crop 10% margin
                height, width = img.shape[:2]
                crop_img = img[int(height*0.1):int(height*0.9), int(width*0.1):int(width*0.9)]
                newFilename = f"static/{filename.split('.')[0]}_cropped.png"
                cv2.imwrite(newFilename, crop_img)
                return newFilename

            case "resize":
                resized_img = cv2.resize(img, (300, 300))
                newFilename = f"static/{filename.split('.')[0]}_resized.png"
                cv2.imwrite(newFilename, resized_img)
                return newFilename

            case "brightness_inc":
                bright_img = cv2.convertScaleAbs(img, alpha=1.2, beta=30)
                newFilename = f"static/{filename.split('.')[0]}_bright_inc.png"
                cv2.imwrite(newFilename, bright_img)
                return newFilename

            case "brightness_dec":
                dark_img = cv2.convertScaleAbs(img, alpha=0.8, beta=-30)
                newFilename = f"static/{filename.split('.')[0]}_bright_dec.png"
                cv2.imwrite(newFilename, dark_img)
                return newFilename

            case "contrast_inc":
                contrast_img = cv2.convertScaleAbs(img, alpha=2.0, beta=0)
                newFilename = f"static/{filename.split('.')[0]}_contrast_inc.png"
                cv2.imwrite(newFilename, contrast_img)
                return newFilename

            case "contrast_dec":
                low_contrast_img = cv2.convertScaleAbs(img, alpha=0.5, beta=0)
                newFilename = f"static/{filename.split('.')[0]}_contrast_dec.png"
                cv2.imwrite(newFilename, low_contrast_img)
                return newFilename


    return None

@app.route("/")
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('signup'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/about")
@login_required
def about():
    return render_template("about.html", title="About")

@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    if request.method == 'POST':
        format_conversion = request.form.get("format_conversion")
        image_processing = request.form.get("image_processing")

        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return render_template("error.html")
        
        file = request.files['file']
        # If the user does not select a file, the browser submits an empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return render_template("error.html")
        elif file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            processed_file = processImage(filename, format_conversion, image_processing)
            
            if processed_file:
                # Get the filename from the processed file path
                download_filename = os.path.basename(processed_file)
                # Send the file for download
                return send_file(
                    processed_file,
                    as_attachment=True,
                    download_name=download_filename,
                    mimetype='image/png'
                )
            else:
                flash('Error processing image')
                return render_template("error.html")
        else:
            flash('File type not allowed. Please upload an image file.')
            return render_template("error.html")
            
    return render_template("index.html")

@app.route("/usage")
@login_required
def usage():
    return render_template("usage.html", title="Usage")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)  # Can specify the port too app.run(debug=True, port=5001)
