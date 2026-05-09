# app/models/user.py
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from datetime import timezone

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)  # 'admin' for Chef, 'user' for Secretary
    facility_location = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    
    def __init__(self, email, role, facility_location, password=None):
      
        self.email = email
        self.role = role
        self.facility_location = facility_location
        if password:
            self.set_password(password)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def is_admin(self):
        return self.role == 'admin'
        

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))