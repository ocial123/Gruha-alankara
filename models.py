from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    designs = db.relationship('Design', backref='author', lazy=True)
    bookings = db.relationship('Booking', backref='customer', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Design(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    selected_theme = db.Column(db.String(50))
    ai_output = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Furniture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255))
    
    bookings = db.relationship('Booking', backref='item', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    furniture_id = db.Column(db.Integer, db.ForeignKey('furniture.id'), nullable=False)
    status = db.Column(db.String(20), default='Pending')
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)