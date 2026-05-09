# app/routes/intern_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app import db
from app.models.intern import Intern
from app.models.attendance import InternAttendance
from app.forms.intern_forms import InternForm
from app.controllers.auth import admin_required 
import os
from app.utils.export_utils import export_model_to_csv, export_model_to_excel
from app.utils.upload_pics import save_picture

intern_bp = Blueprint('intern', __name__, url_prefix='/interns')

@intern_bp.route('/')
@login_required
@admin_required 
def list_interns():
    """List all interns for the current user's facility."""
    page = request.args.get('page', 1, type=int)
    search_term = request.args.get('search', '')

    query = Intern.query.filter_by( is_active = True)

    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            (Intern.first_name.ilike(search_pattern)) |
            (Intern.last_name.ilike(search_pattern)) |
            (Intern.department.ilike(search_pattern)) |
            (Intern.manual_id.ilike(search_pattern)) |
            (Intern.cin.ilike(search_pattern)) |
            (Intern.supervisor.ilike(search_pattern))
        )

    interns = query.order_by(Intern.last_name, Intern.first_name).paginate(page=page, per_page=15)
    return render_template('interns/list_interns.html', interns=interns, search_term=search_term)

@intern_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_intern():
    """Add a new intern."""
    form = InternForm()
    if request.method == 'GET':
        form.facility_location.data = current_user.facility_location

    if form.validate_on_submit():
        # Check uniqueness constraints
        existing_manual_id = Intern.query.filter_by(manual_id=form.manual_id.data).first()
        existing_cin = Intern.query.filter_by(cin=form.cin.data).first()
        existing_rfid = Intern.query.filter_by(rfid_uid=form.rfid_uid.data).first() if form.rfid_uid.data else None

        error = False
        if existing_manual_id:
            flash(f'L\'ID manuel "{form.manual_id.data}" existe déjà.', 'error')
            error = True
        if existing_cin:
            flash(f'Le CIN "{form.cin.data}" existe déjà.', 'error')
            error = True
        if existing_rfid:
            flash(f'Le RFID UID "{form.rfid_uid.data}" est déjà attribué.', 'error')
            error = True
        if error:
            return render_template('interns/add_intern.html', form=form, title="Add Intern")

        picture_filename = None
        if form.picture.data:
            picture_filename = save_picture(form.picture.data)

        new_intern = Intern(
            manual_id=form.manual_id.data,
            rfid_uid=form.rfid_uid.data or None,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            intern_type=form.intern_type.data,
            department=form.department.data,
            cin=form.cin.data,
            supervisor=form.supervisor.data,
            facility_location=form.facility_location.data,
            picture_url=picture_filename,
            is_active=form.is_active.data
        )
        db.session.add(new_intern)
        try:
            db.session.commit()
            flash('Stagiaire ajouté avec succès.', 'success')
            return redirect(url_for('intern.list_interns'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l ajout du stagiaire :{e}', 'error')

    return render_template('interns/add_intern.html', form=form, title="Add Intern")

@intern_bp.route('/edit/<int:intern_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_intern(intern_id):
    """Edit an existing intern."""
    intern = Intern.query.get_or_404(intern_id)
    if intern.facility_location != current_user.facility_location:
         flash('Vous n avez pas la permission de modifier ce stagiaire.', 'danger')
         return redirect(url_for('intern.list_interns'))

    form = InternForm(obj=intern)

    if form.validate_on_submit():
         # Check uniqueness constraints (excluding current intern)
        existing_manual_id = Intern.query.filter(Intern.manual_id == form.manual_id.data, Intern.id != intern_id).first()
        existing_cin = Intern.query.filter(Intern.cin == form.cin.data, Intern.id != intern_id).first()
        existing_rfid = Intern.query.filter(Intern.rfid_uid == form.rfid_uid.data, Intern.id != intern_id).first() if form.rfid_uid.data else None

        error = False
        if existing_manual_id:
            flash(f' ID "{form.manual_id.data}" existe déjà.', 'error')
            error = True
        if existing_cin:
            flash(f'CIN "{form.cin.data}" existe déjà.', 'error')
            error = True
        if existing_rfid:
             flash(f'RFID UID "{form.rfid_uid.data}" Déjà attribué.', 'error')
             error = True

        if error:
             form.picture.data = None # Avoid re-populating file field
             return render_template('interns/edit_intern.html', form=form, title="Edit Intern", intern=intern)

        # Update intern fields
        intern.manual_id = form.manual_id.data
        intern.rfid_uid = form.rfid_uid.data or None
        intern.first_name = form.first_name.data
        intern.last_name = form.last_name.data
        intern.intern_type = form.intern_type.data
        intern.department = form.department.data
        intern.cin = form.cin.data
        intern.supervisor = form.supervisor.data
        intern.facility_location = form.facility_location.data
        intern.is_active = form.is_active.data

        if form.picture.data:
            picture_filename = save_picture(form.picture.data)
            intern.picture_url = picture_filename

        db.session.commit()
        flash('Stagiaire mis à jour avec succès.', 'success')
        return redirect(url_for('intern.list_interns'))

    current_picture_url = intern.picture_url
    return render_template('interns/edit_intern.html', form=form, title="Edit Intern", intern=intern, current_picture_url=current_picture_url)

@intern_bp.route('/delete/<int:intern_id>', methods=['POST'])
@login_required
@admin_required
def delete_intern(intern_id):
    """Delete an intern."""
    intern = Intern.query.get_or_404(intern_id)
    # Optional: Delete picture file
    # ... (similar logic as in delete_supplier) ...

    db.session.delete(intern)
    db.session.commit()
    flash('Stagiaire supprimé avec succès.', 'success')
    return redirect(url_for('intern.list_interns'))

@intern_bp.route('/<int:intern_id>', methods=['GET'])
@login_required
@admin_required
def view_intern(intern_id):
    """View details of a specific intern."""
    intern = Intern.query.get_or_404(intern_id)
    
    attendance_history = InternAttendance.query\
        .filter_by(cin=intern.cin)\
        .order_by(InternAttendance.entry_time.desc())\
        .all()
    
    return render_template('interns/view_intern.html', 
                           intern=intern, 
                           attendance_history=attendance_history)

@intern_bp.route('/export/csv', methods=['GET'])
@login_required
@admin_required
def export_interns_csv():
    """Export all interns data to CSV"""
    search_term = request.args.get('search', '')
    
    query = Intern.query
    
    # Apply filters if search term is provided
    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            (Intern.first_name.ilike(search_pattern)) |
            (Intern.last_name.ilike(search_pattern)) |
            (Intern.department.ilike(search_pattern)) |
            (Intern.manual_id.ilike(search_pattern)) |
            (Intern.cin.ilike(search_pattern)) |
            (Intern.supervisor.ilike(search_pattern))
        )
    
    # Get all results (no pagination)
    interns = query.all()
    
    return export_model_to_csv(interns, 'interns')

@intern_bp.route('/export/excel', methods=['GET'])
@login_required
@admin_required
def export_interns_excel():
    """Export all interns data to Excel"""
    search_term = request.args.get('search', '')
    
    query = Intern.query
    
    # Apply filters if search term is provided
    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            (Intern.first_name.ilike(search_pattern)) |
            (Intern.last_name.ilike(search_pattern)) |
            (Intern.department.ilike(search_pattern)) |
            (Intern.manual_id.ilike(search_pattern)) |
            (Intern.cin.ilike(search_pattern)) |
            (Intern.supervisor.ilike(search_pattern))
        )
    
    # Get all results (no pagination)
    interns = query.all()
    
    return export_model_to_excel(interns, 'interns')