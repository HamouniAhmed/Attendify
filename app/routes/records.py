from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from app.models.attendance import SupplierAttendance, InternAttendance, VisitorAttendance
from app.utils.export_utils import export_model_to_csv, export_model_to_excel
from datetime import datetime, timedelta
from sqlalchemy import desc
from app.controllers.auth import admin_required

records_bp = Blueprint('records', __name__)

@records_bp.route('/attendance/records')
@login_required
@admin_required
def view_records():
    """View attendance records with filtering options"""
    record_type = request.args.get('type', 'supplier')  # Default to supplier records
    
    # Get filter parameters from query string
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    name_filter = request.args.get('name', '')
    location_filter = request.args.get('location', '')
    
    # Additional filters specific to each record type
    company_filter = request.args.get('company', '')
    department_filter = request.args.get('department', '')
    purpose_filter = request.args.get('purpose', '')
    
    # Build base query according to record type
    if record_type == 'supplier':
        query = SupplierAttendance.query
        if start_date:
            query = query.filter(SupplierAttendance.entry_time >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(SupplierAttendance.entry_time < end_date_obj)
        if name_filter:
            query = query.filter(SupplierAttendance.supplier_full_name.ilike(f'%{name_filter}%'))
        if company_filter:
            query = query.filter(SupplierAttendance.company.ilike(f'%{company_filter}%'))
        if location_filter:
            query = query.filter(SupplierAttendance.facility_location.ilike(f'%{location_filter}%'))
        
        records = query.order_by(desc(SupplierAttendance.entry_time)).all()
    
    elif record_type == 'intern':
        query = InternAttendance.query
        if start_date:
            query = query.filter(InternAttendance.entry_time >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(InternAttendance.entry_time < end_date_obj)
        if name_filter:
            query = query.filter(InternAttendance.intern_full_name.ilike(f'%{name_filter}%'))
        if department_filter:
            query = query.filter(InternAttendance.department.ilike(f'%{department_filter}%'))
        if location_filter:
            query = query.filter(InternAttendance.facility_location.ilike(f'%{location_filter}%'))
        
        records = query.order_by(desc(InternAttendance.entry_time)).all()
    
    else:  # visitor
        query = VisitorAttendance.query
        if start_date:
            query = query.filter(VisitorAttendance.entry_time >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(VisitorAttendance.entry_time < end_date_obj)
        if name_filter:
            query = query.filter(VisitorAttendance.visitor_name.ilike(f'%{name_filter}%'))
        if purpose_filter:
            query = query.filter(VisitorAttendance.visit_purpose.ilike(f'%{purpose_filter}%'))
        if location_filter:
            query = query.filter(VisitorAttendance.facility_location.ilike(f'%{location_filter}%'))
        
        records = query.order_by(desc(VisitorAttendance.entry_time)).all()
    
    return render_template('attendance/records.html', 
                          records=records,
                          record_type=record_type,
                          start_date=start_date,
                          end_date=end_date,
                          name_filter=name_filter,
                          company_filter=company_filter,
                          department_filter=department_filter,
                          purpose_filter=purpose_filter,
                          location_filter=location_filter)


@records_bp.route('/attendance/records/export')
@login_required
@admin_required
def export_records():
    """Export attendance records as CSV or Excel"""
    record_type = request.args.get('type', 'supplier')
    export_format = request.args.get('format', 'excel')
    
    # Get filter parameters from query string
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    name_filter = request.args.get('name', '')
    location_filter = request.args.get('location', '')
    
    # Additional filters specific to each record type
    company_filter = request.args.get('company', '')
    department_filter = request.args.get('department', '')
    purpose_filter = request.args.get('purpose', '')
    
    # Build query based on record type
    if record_type == 'supplier':
        query = SupplierAttendance.query
        if start_date:
            query = query.filter(SupplierAttendance.entry_time >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(SupplierAttendance.entry_time < end_date_obj)
        if name_filter:
            query = query.filter(SupplierAttendance.supplier_full_name.ilike(f'%{name_filter}%'))
        if company_filter:
            query = query.filter(SupplierAttendance.company.ilike(f'%{company_filter}%'))
        if location_filter:
            query = query.filter(SupplierAttendance.facility_location.ilike(f'%{location_filter}%'))
        
        records = query.order_by(desc(SupplierAttendance.entry_time)).all()
        filename_prefix = 'supplier_attendance'
    
    elif record_type == 'intern':
        query = InternAttendance.query
        if start_date:
            query = query.filter(InternAttendance.entry_time >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(InternAttendance.entry_time < end_date_obj)
        if name_filter:
            query = query.filter(InternAttendance.intern_full_name.ilike(f'%{name_filter}%'))
        if department_filter:
            query = query.filter(InternAttendance.department.ilike(f'%{department_filter}%'))
        if location_filter:
            query = query.filter(InternAttendance.facility_location.ilike(f'%{location_filter}%'))
        
        records = query.order_by(desc(InternAttendance.entry_time)).all()
        filename_prefix = 'intern_attendance'
    
    else:  # visitor
        query = VisitorAttendance.query
        if start_date:
            query = query.filter(VisitorAttendance.entry_time >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(VisitorAttendance.entry_time < end_date_obj)
        if name_filter:
            query = query.filter(VisitorAttendance.visitor_name.ilike(f'%{name_filter}%'))
        if purpose_filter:
            query = query.filter(VisitorAttendance.visit_purpose.ilike(f'%{purpose_filter}%'))
        if location_filter:
            query = query.filter(VisitorAttendance.facility_location.ilike(f'%{location_filter}%'))
        
        records = query.order_by(desc(VisitorAttendance.entry_time)).all()
        filename_prefix = 'visitor_attendance'
    
    # Export the data using the utility functions
    if export_format == 'csv':
        return export_model_to_csv(records, filename_prefix)
    else:
        return export_model_to_excel(records, filename_prefix)