# app/models/attendance.py
from app import db
import datetime
from datetime import timezone

class SupplierAttendance(db.Model):
    __tablename__ = 'supplier_attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    entry_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(timezone.utc))
    exit_time = db.Column(db.DateTime)
    supplier_full_name = db.Column(db.String(128), nullable=False)
    company = db.Column(db.String(128), nullable=False)
    cin = db.Column(db.String(64), nullable=False)
    presence_type = db.Column(db.String(20), nullable=False)  # Visit or Intervention
    department_visited = db.Column(db.String(64), nullable=False)
    person_visited = db.Column(db.String(128), nullable=False)
    facility_location = db.Column(db.String(128), nullable=False)
    hours_spent = db.Column(db.Float)
    checked_in_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    checked_out_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    notes = db.Column(db.Text)
    
    def __init__(self, supplier_full_name, company, cin, presence_type, department_visited, 
                 person_visited, facility_location, checked_in_by, entry_time=None):
        self.supplier_full_name = supplier_full_name
        self.company = company
        self.cin = cin
        self.presence_type = presence_type
        self.department_visited = department_visited
        self.person_visited = person_visited
        self.facility_location = facility_location
        self.checked_in_by = checked_in_by
        if entry_time:
            self.entry_time = entry_time
    
    def check_out(self, checked_out_by):
        self.exit_time = datetime.datetime.now(timezone.utc)
        self.checked_out_by = checked_out_by
        self.calculate_hours()
    
    def calculate_hours(self):
        if self.exit_time and self.entry_time:
            time_diff = self.exit_time - self.entry_time
            self.hours_spent = time_diff.total_seconds() / 3600  # Convert to hours
    
    def __repr__(self):
        return f'<SupplierAttendance {self.supplier_full_name} at {self.entry_time}>'


class InternAttendance(db.Model):
    __tablename__ = 'intern_attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    entry_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(timezone.utc))
    exit_time = db.Column(db.DateTime)
    intern_full_name = db.Column(db.String(128), nullable=False)
    department = db.Column(db.String(64), nullable=False)
    cin = db.Column(db.String(64), nullable=False)
    intern_type = db.Column(db.String(64), nullable=False)
    facility_location = db.Column(db.String(128), nullable=False)
    hours_spent = db.Column(db.Float)
    checked_in_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    checked_out_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    notes = db.Column(db.Text)
    
    def __init__(self, intern_full_name, department, cin, intern_type, facility_location, 
                 checked_in_by, entry_time=None):
        self.intern_full_name = intern_full_name
        self.department = department
        self.cin = cin
        self.intern_type = intern_type
        self.facility_location = facility_location
        self.checked_in_by = checked_in_by
        if entry_time:
            self.entry_time = entry_time
    
    def check_out(self, checked_out_by):
        self.exit_time = datetime.datetime.now(timezone.utc)
        self.checked_out_by = checked_out_by
        self.calculate_hours()
    
    def calculate_hours(self):
        if self.exit_time and self.entry_time:
            time_diff = self.exit_time - self.entry_time
            self.hours_spent = time_diff.total_seconds() / 3600  # Convert to hours
    
    def __repr__(self):
        return f'<InternAttendance {self.intern_full_name} at {self.entry_time}>'


class VisitorAttendance(db.Model):
    __tablename__ = 'visitor_attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    entry_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(timezone.utc))
    exit_time = db.Column(db.DateTime)
    visitor_name = db.Column(db.String(128), nullable=False)
    visit_purpose = db.Column(db.String(256), nullable=False)
    visit_host = db.Column(db.String(128), nullable=False)  # School, company, establishment, etc.
    facility_location = db.Column(db.String(128), nullable=False)
    hours_spent = db.Column(db.Float)
    checked_in_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    checked_out_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    notes = db.Column(db.Text)
    
    def __init__(self, visitor_name, visit_purpose, visit_host, facility_location, 
                 checked_in_by, entry_time=None):
        self.visitor_name = visitor_name
        self.visit_purpose = visit_purpose
        self.visit_host = visit_host
        self.facility_location = facility_location
        self.checked_in_by = checked_in_by
        if entry_time:
            self.entry_time = entry_time
    
    def check_out(self, checked_out_by):
        self.exit_time = datetime.datetime.now(timezone.utc)
        self.checked_out_by = checked_out_by
        self.calculate_hours()
    
    def calculate_hours(self):
        if self.exit_time and self.entry_time:
            time_diff = self.exit_time - self.entry_time
            self.hours_spent = time_diff.total_seconds() / 3600  # Convert to hours
    
    def __repr__(self):
        return f'<VisitorAttendance {self.visitor_name} at {self.entry_time}>'