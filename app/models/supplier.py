# app/models/supplier.py
from app import db
import datetime
from datetime import timezone

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    manual_id = db.Column(db.String(64), unique=True, nullable=False)
    rfid_uid = db.Column(db.String(64), unique=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    company = db.Column(db.String(128), nullable=False)
    cin = db.Column(db.String(64), unique=True, nullable=False)
    chef_name = db.Column(db.String(128))
    chef_number = db.Column(db.String(64))
    cnss = db.Column(db.String(64))
    picture_url = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(timezone.utc), onupdate=datetime.datetime.now(timezone.utc))
    facility_location = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    def __init__(self, manual_id, first_name, last_name, company, cin, facility_location, 
                 rfid_uid=None, chef_name=None, chef_number=None, cnss=None, picture_url=None, is_active=True):
        self.manual_id = manual_id
        self.rfid_uid = rfid_uid
        self.first_name = first_name
        self.last_name = last_name
        self.company = company
        self.cin = cin
        self.chef_name = chef_name
        self.chef_number = chef_number
        self.cnss = cnss
        self.picture_url = picture_url
        self.facility_location = facility_location
        self.is_active = is_active
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<Supplier {self.full_name} - {self.company}>'