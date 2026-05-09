# app/models/intern.py
from app import db
import datetime
from datetime import timezone

class Intern(db.Model):
    __tablename__ = 'interns'
    
    id = db.Column(db.Integer, primary_key=True)
    manual_id = db.Column(db.String(64), unique=True, nullable=False)
    rfid_uid = db.Column(db.String(64), unique=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    intern_type = db.Column(db.String(64), nullable=False)  # e.g., Summer, Co-op, etc.
    department = db.Column(db.String(64), nullable=False)
    cin = db.Column(db.String(64), unique=True, nullable=False)
    supervisor = db.Column(db.String(128), nullable=False)
    picture_url = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(timezone.utc), onupdate=datetime.datetime.now(timezone.utc))
    facility_location = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    def __init__(self, manual_id, first_name, last_name, intern_type, department, cin, 
                 supervisor, facility_location, rfid_uid=None, picture_url=None, is_active =True):
        self.manual_id = manual_id
        self.rfid_uid = rfid_uid
        self.first_name = first_name
        self.last_name = last_name
        self.intern_type = intern_type
        self.department = department
        self.cin = cin
        self.supervisor = supervisor
        self.picture_url = picture_url
        self.facility_location = facility_location
        self.is_active = is_active 
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<Intern {self.full_name} - {self.department}>'