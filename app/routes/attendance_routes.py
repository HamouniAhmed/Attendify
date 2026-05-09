
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, Response 
from flask_login import login_required, current_user
from app import db
from app.controllers.attendance_controller import process_attendance, record_intern_attendance, record_supplier_attendance, record_visitor_attendance, check_out_attendance, get_daily_stats, get_recent_attendance, get_person_by_id, get_person_by_cin, get_active_attendance
from sqlalchemy import or_ 
from app.forms.attendance_forms import AttendanceCheckForm, VisitorRegistrationForm, SupplierAttendanceForm
from app.models.attendance import InternAttendance, SupplierAttendance, VisitorAttendance
import datetime
import io
import pandas as pd
attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendance', methods=['GET'])
@login_required
def attendance_home():
    """Main attendance page with check-in/out functionality"""
    check_form = AttendanceCheckForm()
    visitor_form = VisitorRegistrationForm()
    supplier_form = SupplierAttendanceForm()

    check_form.facility_location.data = current_user.facility_location
    
    # Get today's stats and recent entries
    stats = get_daily_stats()
    recent = get_recent_attendance(5)  # Show 5 most recent entries
    
    return render_template('attendance/attendance_home.html', 
                          check_form=check_form,
                          visitor_form=visitor_form,
                          supplier_form=supplier_form,
                          stats=stats,
                          recent=recent,
                          )

@attendance_bp.route('/attendance/process', methods=['POST'])
@login_required
def process_attendance_request():
    """Process an attendance check-in/out request"""
    form = AttendanceCheckForm()
    
    if form.validate_on_submit():
        id_value = form.id_value.data
        facility_location = form.facility_location.data
        
        # First try to find by ID/RFID
        result_type, data = process_attendance(id_value)
        
        # If not found, try by CIN
        if result_type == 'not_found':
            person_type, person = get_person_by_cin(id_value)
            
            if person:
                # Handle by person type
                if person_type == 'intern':
                    # Check if already checked in
                    person_identifier = f"{person.first_name} {person.last_name}"
                    active_attendance = get_active_attendance('intern', person_identifier)
                    
                    if active_attendance:
                        # Already checked in, process checkout
                        result = check_out_attendance('intern', active_attendance.id, current_user.id)
                        if result:
                            flash(f'Sortie enregistré pour {result.intern_full_name}', 'success')
                            return redirect(url_for('attendance.attendance_home'))
                        else:
                            flash('Erreur lors du traitement du départ', 'danger')
                            return redirect(url_for('attendance.attendance_home'))
                    else:
                        # Not checked in, process check-in
                        attendance = record_intern_attendance(
                            person, 
                            facility_location, 
                            current_user.id
                        )
                        flash(f'Arrivée enregistrée pour {person.first_name} {person.last_name}', 'success')
                        return redirect(url_for('attendance.attendance_home'))
                
                elif person_type == 'supplier':
                    # Check if already checked in
                    person_identifier = f"{person.first_name} {person.last_name}"
                    active_attendance = get_active_attendance('supplier', person_identifier)
                    
                    if active_attendance:
                        # Already checked in, process checkout
                        result = check_out_attendance('supplier', active_attendance.id, current_user.id)
                        if result:
                            flash(f'Sortie enregistré pour {result.supplier_full_name}', 'success')
                            return redirect(url_for('attendance.attendance_home'))
                        else:
                            flash('Erreur lors du traitement du départ', 'danger')
                            return redirect(url_for('attendance.attendance_home'))
                    else:
                        # Need more info for supplier check-in
                        flash('Veuillez fournir des détails supplémentaires pour l\'enregistrement du fournisseur', 'info')
                        return redirect(url_for('attendance.attendance_home', 
                                              show_supplier_form='true', 
                                              supplier_id=person.manual_id,
                                              facility_location=facility_location))
            else:
                # Still not found
                flash('ID ou CIN non trouvé dans le système. Ajouter comme visiteur?', 'warning')
                return redirect(url_for('attendance.attendance_home'))
        
        # Continue with original process_attendance logic
        elif result_type == 'checked_out':
            # Person is already checked in, perform checkout
            attendance_type = 'intern' if isinstance(data, InternAttendance) else 'supplier'
            result = check_out_attendance(attendance_type, data.id, current_user.id)
            
            if result:
                flash(f'Sortie enregistré pour {result.intern_full_name if attendance_type == "intern" else result.supplier_full_name}', 'success')
            else:
                flash('Erreur lors du traitement du départ', 'danger')
            return redirect(url_for('attendance.attendance_home'))
        
        elif result_type == 'checked_in':
            # Intern check-in (supplier needs more info)
            if hasattr(data, 'intern_type'):  # This is an Intern
                attendance = record_intern_attendance(
                    data, 
                    facility_location, 
                    current_user.id
                )
                flash(f'Arrivée enregistrée pour {data.first_name} {data.last_name}', 'success')
                return redirect(url_for('attendance.attendance_home'))
        
        elif result_type == 'check_in_supplier':
            # We need more info for supplier check-in
            flash('Veuillez fournir des détails supplémentaires pour l\'enregistrement du fournisseur', 'info')
            return redirect(url_for('attendance.attendance_home', 
                                   show_supplier_form='true', 
                                   supplier_id=id_value,
                                   facility_location=facility_location))
    
    flash('Erreur de traitement. Veuillez réessayer.', 'danger')
    return redirect(url_for('attendance.attendance_home'))

@attendance_bp.route('/attendance/supplier/checkin', methods=['POST'])
@login_required
def supplier_checkin():
    """Process supplier check-in with additional details"""
    form = SupplierAttendanceForm()
    
    if form.validate_on_submit():
        supplier_id = request.form.get('supplier_id')
        facility_location = request.form.get('facility_location')
        
        if not supplier_id:
            flash('Identifiant du fournisseur manquant.', 'danger')
            return redirect(url_for('attendance.attendance_home'))
        
        person_type, supplier = get_person_by_id(supplier_id)
        
        if person_type != 'supplier' or not supplier:
            flash('Fournisseur non trouvé.', 'danger')
            return redirect(url_for('attendance.attendance_home'))
        
        attendance = record_supplier_attendance(
            supplier,
            facility_location,
            form.presence_type.data,
            form.department_visited.data,
            form.person_visited.data,
            current_user.id,
            form.notes.data
        )
        
        flash(f'Arrivée enregistrée pour {supplier.first_name} {supplier.last_name}', 'success')
    else:
        flash('Données du formulaire invalides. Veuillez vérifier vos saisies.', 'danger')
    
    return redirect(url_for('attendance.attendance_home'))

@attendance_bp.route('/attendance/visitor/add', methods=['GET' ,'POST' ])
@login_required
def add_visitor():
    """Add and check in a visitor"""
    form = VisitorRegistrationForm()
    check_form = AttendanceCheckForm()
    supplier_form = SupplierAttendanceForm()

    stats = get_daily_stats()
    recent = get_recent_attendance(5)

    if request.method == 'POST':
        # ad visitor from the fashed msg if not exists in db 
        if form.validate_on_submit():
            attendance = record_visitor_attendance(
                form.visitor_name.data,
                form.visit_purpose.data,
                form.visit_host.data,
                form.facility_location.data,
                current_user.id,
                form.notes.data
            )
            flash(f'Visiteur enregistré et pointé avec succès.: {form.visitor_name.data}', 'success')
        else:
            flash('Données du formulaire invalides. Veuillez vérifier vos saisies.', 'danger')
    # add visitor from the navbar 
    elif request.method == 'GET':
        return render_template('attendance/attendance_home.html', 
                               visitor_form=form,
                               check_form=check_form,
                               supplier_form=supplier_form,
                               stats=stats, 
                               show_visitor_modal=True)
    
    return redirect(url_for('attendance.attendance_home'))

@attendance_bp.route('/attendance/checkout/<attendance_type>/<int:attendance_id>', methods=['POST'])
@login_required
def checkout(attendance_type, attendance_id):
    """Check out a person who is already checked in"""
    if attendance_type not in ['intern', 'supplier', 'visitor']:
        flash('Type de présence invalide.', 'danger')
        return redirect(url_for('attendance.attendance_home')) # Consider changing this redirect
    
    attendance = check_out_attendance(attendance_type, attendance_id, current_user.id)
    
    if attendance:
        # This getattr logic seems correct based on your prepare_..._data functions
        # (e.g., InternAttendance has intern_full_name, VisitorAttendance has visitor_name)
        name_attribute_suffix = 'full_name' if attendance_type != 'visitor' else 'name'
        name_accessor = f"{attendance_type}_{name_attribute_suffix}" # e.g., "intern_full_name" or "visitor_name"
        
        name_to_display = "Personne" # Default
        if hasattr(attendance, name_accessor):
            name_to_display = getattr(attendance, name_accessor, f"{attendance_type.capitalize()} ID: {attendance.id}")
        else: # Fallback if the specific composite attribute isn't found
             name_to_display = f"{attendance_type.capitalize()} (ID: {attendance.id})"

        flash(f'Sortie effectuée avec succès pour {name_to_display}.', 'success')
    else:
        flash('Erreur lors du traitement de la sortie ou enregistrement non trouvé/déjà sorti.', 'danger')
    
    # SUGGESTION: Redirect back to the details page for better UX
    return redirect(request.referrer or url_for('attendance.attendance_details'))
    # OLD: return redirect(url_for('attendance.attendance_home'))



@attendance_bp.route('/attendance/details', methods=['GET'])
@login_required
def attendance_details():
    """Show detailed attendance records with filtering options, including those still checked in."""
    today = datetime.datetime.now().date()
    start_date_str = request.args.get('start_date', today.strftime('%Y-%m-%d'))
    end_date_str = request.args.get('end_date', today.strftime('%Y-%m-%d'))
    attendance_type_filter = request.args.get('type', 'all') # Renamed to avoid conflict
    facility = request.args.get('facility', 'all')
    
    try:
        start_date_obj = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date_obj = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        start_date_obj = today
        end_date_obj = today
        flash("Dates invalides, affichage des données pour aujourd'hui.", "warning")

    # For querying, we want to include the entire end_date_obj
    query_end_date_obj = end_date_obj + datetime.timedelta(days=1)
    
    start_datetime = datetime.datetime.combine(start_date_obj, datetime.time.min)
    # end_datetime will be the beginning of the day *after* the selected end_date_obj
    end_datetime_for_range_query = datetime.datetime.combine(query_end_date_obj, datetime.time.min) 
    
    records_list = []

    def get_records_for_type(model_class, type_name_str):
        # Condition 1: Entered within the selected date range (checked in or out).
        # Condition 2: Entered BEFORE the start_datetime of the range AND exit_time is NULL (still active).
        query = model_class.query.filter(
            or_(
                (model_class.entry_time >= start_datetime) & (model_class.entry_time < end_datetime_for_range_query),
                (model_class.entry_time < start_datetime) & (model_class.exit_time == None)
            )
        )
        
        if facility != 'all':
            query = query.filter_by(facility_location=facility)
        
        results = query.all()
        for r in results:
            r.attendance_type = type_name_str # Crucial: Add type attribute for the template
        return results

    if attendance_type_filter == 'intern' or attendance_type_filter == 'all':
        records_list.extend(get_records_for_type(InternAttendance, 'intern'))
    
    if attendance_type_filter == 'supplier' or attendance_type_filter == 'all':
        records_list.extend(get_records_for_type(SupplierAttendance, 'supplier'))
        
    if attendance_type_filter == 'visitor' or attendance_type_filter == 'all':
        records_list.extend(get_records_for_type(VisitorAttendance, 'visitor'))

    # Sort all collected records by entry_time
    records_list.sort(key=lambda x: x.entry_time, reverse=True)
    
    return render_template('attendance/details.html', 
                           records=records_list,
                           start_date=start_date_obj.strftime('%Y-%m-%d'),
                           end_date=end_date_obj.strftime('%Y-%m-%d'), # Display original selected end date
                           selected_type=attendance_type_filter,
                           selected_facility=facility)

@attendance_bp.route('/attendance/export/<format>', methods=['GET'])
@login_required
def export_data(format):
    """Export attendance data in CSV or Excel format with applied filters"""
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    attendance_type = request.args.get('type', 'all')
    facility = request.args.get('facility', 'all')
    
    today = datetime.datetime.now().date()
    
    # Convert string dates to datetime
    try:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else today
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else today
        end_date = end_date + datetime.timedelta(days=1)  # Include the end date
    except ValueError:
        start_date = today
        end_date = today + datetime.timedelta(days=1)
    
    start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
    end_datetime = datetime.datetime.combine(end_date, datetime.time.min)
    
    # Base queries with date filter
    intern_query = InternAttendance.query.filter(
        InternAttendance.entry_time >= start_datetime,
        InternAttendance.entry_time < end_datetime
    )
    
    supplier_query = SupplierAttendance.query.filter(
        SupplierAttendance.entry_time >= start_datetime,
        SupplierAttendance.entry_time < end_datetime
    )
    
    visitor_query = VisitorAttendance.query.filter(
        VisitorAttendance.entry_time >= start_datetime,
        VisitorAttendance.entry_time < end_datetime
    )
    
    # Apply facility filter if not 'all'
    if facility != 'all':
        intern_query = intern_query.filter_by(facility_location=facility)
        supplier_query = supplier_query.filter_by(facility_location=facility)
        visitor_query = visitor_query.filter_by(facility_location=facility)
    
    # Get records based on type filter
    if attendance_type == 'intern':
        records = intern_query.order_by(InternAttendance.entry_time.desc()).all()
        export_data = prepare_intern_data(records)
    elif attendance_type == 'supplier':
        records = supplier_query.order_by(SupplierAttendance.entry_time.desc()).all()
        export_data = prepare_supplier_data(records)
    elif attendance_type == 'visitor':
        records = visitor_query.order_by(VisitorAttendance.entry_time.desc()).all()
        export_data = prepare_visitor_data(records)
    else:  # all types
        interns = intern_query.all()
        suppliers = supplier_query.all()
        visitors = visitor_query.all()
        export_data = prepare_all_data(interns, suppliers, visitors)
    
    # Create DataFrame
    df = pd.DataFrame(export_data)
    
    # Create buffer for file
    buffer = io.BytesIO()
    
    # Export to requested format
    if format == 'csv':
        df.to_csv(buffer, index=False, encoding='utf-8')
        mimetype = 'text/csv'
        filename = f'attendance_export_{start_date.strftime("%Y%m%d")}_to_{(end_date - datetime.timedelta(days=1)).strftime("%Y%m%d")}.csv'
    elif format == 'excel':
        df.to_excel(buffer, index=False, engine='openpyxl')
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        filename = f'attendance_export_{start_date.strftime("%Y%m%d")}_to_{(end_date - datetime.timedelta(days=1)).strftime("%Y%m%d")}.xlsx'
    else:
        flash('Format non supporté', 'danger')
        return redirect(url_for('attendance.attendance_details'))
    
    buffer.seek(0)
    
    # Return file as response
    return Response(
        buffer,
        mimetype=mimetype,
        headers={'Content-Disposition': f'attachment;filename={filename}'}
    )

def prepare_intern_data(records):
    """Prepare intern attendance data for export"""
    data = []
    for record in records:
        data.append({
            'Nom': record.intern_full_name,
            'Type': 'Stagiaire',
            'Site': record.facility_location,
            'Entrée': record.entry_time.strftime('%Y-%m-%d %H:%M:%S') if record.entry_time else '-',
            'Sortie': record.exit_time.strftime('%Y-%m-%d %H:%M:%S') if record.exit_time else '-',
            'Heures': f"{record.hours_spent:.2f}" if record.hours_spent is not None else '-',
            'Département': record.department,
            'Type de Stage': record.intern_type,
            'CIN': record.cin,
            'Notes': record.notes
        })
    return data

def prepare_supplier_data(records):
    """Prepare supplier attendance data for export"""
    data = []
    for record in records:
        data.append({
            'Nom': record.supplier_full_name,
            'Type': 'Fournisseur',
            'Site': record.facility_location,
            'Entrée': record.entry_time.strftime('%Y-%m-%d %H:%M:%S') if record.entry_time else '-',
            'Sortie': record.exit_time.strftime('%Y-%m-%d %H:%M:%S') if record.exit_time else '-',
            'Heures': f"{record.hours_spent:.2f}" if record.hours_spent is not None else '-',
            'Entreprise': record.company,
            'Type de Présence': record.presence_type,
            'Département Visité': record.department_visited,
            'Personne Visitée': record.person_visited,
            'CIN': record.cin,
            'Notes': record.notes
        })
    return data

def prepare_visitor_data(records):
    """Prepare visitor attendance data for export"""
    data = []
    for record in records:
        data.append({
            'Nom': record.visitor_name,
            'Type': 'Visiteur',
            'Site': record.facility_location,
            'Entrée': record.entry_time.strftime('%Y-%m-%d %H:%M:%S') if record.entry_time else '-',
            'Sortie': record.exit_time.strftime('%Y-%m-%d %H:%M:%S') if record.exit_time else '-',
            'Heures': f"{record.hours_spent:.2f}" if record.hours_spent is not None else '-',
            'Raison de la Visite': record.visit_purpose,
            'Hôte': record.visit_host,
            'Notes': record.notes
        })
    return data

def prepare_all_data(interns, suppliers, visitors):
    """Prepare combined data for export"""
    intern_data = prepare_intern_data(interns)
    supplier_data = prepare_supplier_data(suppliers)
    visitor_data = prepare_visitor_data(visitors)
    
    # Ensure all records have the same columns by filling missing keys with empty values
    all_keys = set()
    for data_list in [intern_data, supplier_data, visitor_data]:
        for item in data_list:
            all_keys.update(item.keys())
    
    for data_list in [intern_data, supplier_data, visitor_data]:
        for item in data_list:
            for key in all_keys:
                if key not in item:
                    item[key] = '-'
    
    # Combine all records
    combined_data = intern_data + supplier_data + visitor_data
    
    # Sort by entry time (descending)
    # This assumes that 'Entrée' field is present and in a consistent format
    def get_entry_time(item):
        entry = item.get('Entrée')
        if entry and entry != '-':
            try:
                return datetime.datetime.strptime(entry, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass
        return datetime.datetime.min
    
    combined_data.sort(key=get_entry_time, reverse=True)
    
    return combined_data