from flask import flash, current_app
from app import db
from app.models.intern import Intern
from app.models.supplier import Supplier
from app.models.attendance import InternAttendance, SupplierAttendance, VisitorAttendance
import datetime

def get_person_by_id(id_value):
    """
    Find a person (intern or supplier) by their ID
    Returns tuple (person_type, person_data)
    """
    # First check if it's an intern
    intern = Intern.query.filter((Intern.manual_id == id_value) | (Intern.rfid_uid == id_value)).first()
    if intern:
        return ('intern', intern)
    
    # Then check if it's a supplier
    supplier = Supplier.query.filter((Supplier.manual_id == id_value) | (Supplier.rfid_uid == id_value)).first()
    if supplier:
        return ('supplier', supplier)
    
    return (None, None)

def get_active_attendance(person_type, person_identifier):
    """Check if person has an active check-in without checkout"""
    if person_type == 'intern':
        return InternAttendance.query.filter_by(
            intern_full_name=person_identifier,
            exit_time=None
        ).first()
    elif person_type == 'supplier':
        return SupplierAttendance.query.filter_by(
            supplier_full_name=person_identifier,
            exit_time=None
        ).first()
    return None

def process_attendance(id_value):
    """
    Process an attendance request
    Returns tuple (result_type, data)
    where result_type is:
    - 'check_in_supplier' - needs additional info before check-in
    - 'checked_in' - successfully checked in
    - 'checked_out' - successfully checked out
    - 'not_found' - ID not found
    """
    person_type, person = get_person_by_id(id_value)
    
    if not person:
        return ('not_found', None)
    
    # Determine person identifier based on type
    if person_type == 'intern':
        person_identifier = f"{person.first_name} {person.last_name}"
        active_attendance = get_active_attendance('intern', person_identifier)
        
        if active_attendance:
            # Person is already checked in, perform checkout
            return ('checked_out', active_attendance)
        else:
            # Perform check-in
            return ('checked_in', person)
    
    elif person_type == 'supplier':
        person_identifier = f"{person.first_name} {person.last_name}"
        active_attendance = get_active_attendance('supplier', person_identifier)
        
        if active_attendance:
            # Supplier is already checked in, perform checkout
            return ('checked_out', active_attendance)
        else:
            # Supplier needs more details before check-in
            return ('check_in_supplier', person)
    
    return ('not_found', None)

def record_intern_attendance(intern, facility_location, user_id, notes=None):
    """Record a new intern attendance entry"""
    attendance = InternAttendance(
        intern_full_name=f"{intern.first_name} {intern.last_name}",
        department=intern.department,
        cin=intern.cin,
        intern_type=intern.intern_type,
        facility_location=facility_location,
        checked_in_by=user_id
    )
    
    if notes:
        attendance.notes = notes
    
    db.session.add(attendance)
    db.session.commit()
    return attendance

def record_supplier_attendance(supplier, facility_location, presence_type, 
                              department_visited, person_visited, user_id, notes=None):
    """Record a new supplier attendance entry"""
    attendance = SupplierAttendance(
        supplier_full_name=f"{supplier.first_name} {supplier.last_name}",
        company=supplier.company,
        cin=supplier.cin,
        presence_type=presence_type,
        department_visited=department_visited,
        person_visited=person_visited,
        facility_location=facility_location,
        checked_in_by=user_id
    )
    
    if notes:
        attendance.notes = notes
    
    db.session.add(attendance)
    db.session.commit()
    return attendance

def record_visitor_attendance(visitor_name, visit_purpose, visit_host, 
                             facility_location, user_id, notes=None):
    """Record a new visitor attendance entry"""
    attendance = VisitorAttendance(
        visitor_name=visitor_name,
        visit_purpose=visit_purpose,
        visit_host=visit_host,
        facility_location=facility_location,
        checked_in_by=user_id
    )
    
    if notes:
        attendance.notes = notes
    
    db.session.add(attendance)
    db.session.commit()
    return attendance

def check_out_attendance(attendance_type, attendance_id, user_id):
    """Process checkout for an attendance record"""
    if attendance_type == 'intern':
        attendance = InternAttendance.query.get(attendance_id)
    elif attendance_type == 'supplier':
        attendance = SupplierAttendance.query.get(attendance_id)
    elif attendance_type == 'visitor':
        attendance = VisitorAttendance.query.get(attendance_id)
    else:
        return None
    
    if attendance and not attendance.exit_time:
        attendance.check_out(user_id)
        db.session.commit()
        return attendance
    
    return None

def get_daily_stats():
    """Get attendance statistics for today"""
    today = datetime.datetime.now().date()
    tomorrow = today + datetime.timedelta(days=1)
    today_start = datetime.datetime.combine(today, datetime.time.min)
    today_end = datetime.datetime.combine(tomorrow, datetime.time.min)
    
    # Count today's attendance
    intern_count = InternAttendance.query.filter(
        InternAttendance.entry_time >= today_start,
        InternAttendance.entry_time < today_end
    ).count()
    
    supplier_count = SupplierAttendance.query.filter(
        SupplierAttendance.entry_time >= today_start,
        SupplierAttendance.entry_time < today_end
    ).count()
    
    visitor_count = VisitorAttendance.query.filter(
        VisitorAttendance.entry_time >= today_start,
        VisitorAttendance.entry_time < today_end
    ).count()
    
    # Get currently checked in (no exit time)
    current_interns = InternAttendance.query.filter(
        InternAttendance.exit_time == None
    ).all()
    
    current_suppliers = SupplierAttendance.query.filter(
        SupplierAttendance.exit_time == None
    ).all()
    
    current_visitors = VisitorAttendance.query.filter(
        VisitorAttendance.exit_time == None
    ).all()
    
    return {
        'today': {
            'interns': intern_count,
            'suppliers': supplier_count,
            'visitors': visitor_count,
            'total': intern_count + supplier_count + visitor_count
        },
        'current': {
            'interns': current_interns,
            'suppliers': current_suppliers,
            'visitors': current_visitors,
            'total': len(current_interns) + len(current_suppliers) + len(current_visitors)
        }
    }

def get_recent_attendance(limit=10):
    """Get most recent attendance records"""
    intern_entries = InternAttendance.query.order_by(InternAttendance.entry_time.desc()).limit(limit).all()
    supplier_entries = SupplierAttendance.query.order_by(SupplierAttendance.entry_time.desc()).limit(limit).all()
    visitor_entries = VisitorAttendance.query.order_by(VisitorAttendance.entry_time.desc()).limit(limit).all()
    
    # Combine and sort by entry time
    all_entries = intern_entries + supplier_entries + visitor_entries
    all_entries.sort(key=lambda x: x.entry_time, reverse=True)
    
    return all_entries[:limit]

def get_person_by_cin(cin_value):
    """
    Find a person (intern or supplier) by their CIN
    Returns tuple (person_type, person_data)
    """
    # First check if it's an intern
    intern = Intern.query.filter_by(cin=cin_value).first()
    if intern:
        return ('intern', intern)
    
    # Then check if it's a supplier
    supplier = Supplier.query.filter_by(cin=cin_value).first()
    if supplier:
        return ('supplier', supplier)
    
    return (None, None)