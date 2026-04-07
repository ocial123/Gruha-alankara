import os
from flask_caching import Cache
import uuid
import json
from ai_agent import process_room_design
from cv_analyzer import analyze_room_image
from flask import Flask, render_template, request, redirect, url_for, flash, session
from config import Config
from models import db, User, Design, Furniture, Booking

# 1. Create the app first
app = Flask(__name__)

# Configure Redis Caching
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_REDIS_HOST'] = 'localhost'
app.config['CACHE_REDIS_PORT'] = 6379
app.config['CACHE_DEFAULT_TIMEOUT'] = 3600 # Cache results for 1 hour

cache = Cache(app)

# 3. Apply the rest of the configurations
app.config.from_object(Config)
db.init_app(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# 1. Update your app_context to add dummy furniture data
with app.app_context():
    db.create_all()
    # Seed furniture if the table is empty
    if not Furniture.query.first():
        sample_items = [
            Furniture(name="Sleek Leather Sofa", category="Modern", price=45000),
            Furniture(name="Glass Center Table", category="Modern", price=15000),
            Furniture(name="Rattan Chair", category="Bohemian", price=8500),
            Furniture(name="Vintage Persian Rug", category="Bohemian", price=12000),
            Furniture(name="Industrial Metal Lamp", category="Industrial", price=3500)
        ]
        db.session.add_all(sample_items)
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists.', 'error')
            return redirect(url_for('register'))
        
        # Create and save the new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Verify credentials
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.user_id
            session['username'] = user.username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('design'))
        else:
            flash('Invalid email or password.', 'error')
            
    return render_template('login.html')
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/design')
def design():
    if 'user_id' not in session:
        flash("Please log in to create a design.", "error")
        return redirect(url_for('login'))
    return render_template('design.html')

@app.route('/upload', methods=['POST'])
def upload():
    # ... your existing upload logic ...
    if 'user_id' not in session:
        return {"error": "Unauthorized. Please log in."}, 401

    if 'image' not in request.files:
        return {"error": "No image provided."}, 400
        
    file = request.files['image']
    theme = request.form.get('theme', 'Modern')
    language = request.form.get('language', 'en') # Support for multilingual
    
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Analyze image with CV Analyzer
        cv_result = analyze_room_image(filepath)
        if not cv_result.get("is_room"):
            return {"error": cv_result.get("error", "Image is not recognized as a valid room.")}, 400
            
        # Trigger the AI pipeline
        ai_text, audio_file, ai_image = process_room_design(filename, theme, language)
        
        # Update database
        new_design = Design(
            user_id=session['user_id'], 
            image_path=filename,
            selected_theme=theme,
            ai_output=ai_text
        )
        db.session.add(new_design)
        db.session.commit()
        
        # Redirect to the result page (we will build this next)
        return {"redirect": url_for('result', design_id=new_design.id)}, 200
        
    return {"error": "Invalid file type."}, 400

@app.route('/book/<int:furniture_id>', methods=['POST'])
def book(furniture_id):
    if 'user_id' not in session:
        flash("Please log in to book items.", "error")
        return redirect(url_for('login'))
        
    # Create a new booking
    new_booking = Booking(
        user_id=session['user_id'], 
        furniture_id=furniture_id, 
        status='Confirmed'
    )
    db.session.add(new_booking)
    db.session.commit()
    
    flash("Item successfully booked via Buddy AI!", "success")
    # Send them back to the results page they were just on
    return redirect(request.referrer or url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in to view your dashboard.", "error")
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    
    # Fetch designs and bookings for the logged-in user, newest first
    user_designs = Design.query.filter_by(user_id=user_id).order_by(Design.id.desc()).all()
    user_bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.id.desc()).all()
    
    return render_template('dashboard.html', designs=user_designs, bookings=user_bookings)

# 2. Update your result route to fetch recommendations

@app.route('/result/<int:design_id>')
def result(design_id):
    if 'user_id' not in session:
        flash("Please log in.", "error")
        return redirect(url_for('login'))
    
    design = Design.query.get_or_404(design_id)
    
    # NEW: Parse the AI JSON string safely
    try:
        ai_data = json.loads(design.ai_output)
        display_text = ai_data.get('recommendations', design.ai_output)
    except:
        display_text = design.ai_output
        
    recommendations = Furniture.query.filter_by(category=design.selected_theme).all()
    
    return render_template('result.html', design=design, furniture=recommendations, ai_text=display_text)
if __name__ == '__main__':
    app.run(debug=True)