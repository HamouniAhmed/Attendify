# app/routes/supplier_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file
from flask_login import login_required, current_user
from app import db
from app.models.supplier import Supplier
from app.models.attendance import SupplierAttendance
from app.forms.supplier_forms import SupplierForm
from app.controllers.auth import admin_required # Assuming admin is required
from app.utils.export_utils import export_model_to_csv, export_model_to_excel
from app.utils.upload_pics import save_picture
supplier_bp = Blueprint('supplier', __name__, url_prefix='/suppliers')

@supplier_bp.route('/')
@login_required
@admin_required # Apply decorator if needed
def list_suppliers():
    """List all suppliers for the current user's facility."""
    page = request.args.get('page', 1, type=int)
    search_term = request.args.get('search', '')

    query = Supplier.query.filter_by(facility_location=current_user.facility_location)

    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            (Supplier.first_name.ilike(search_pattern)) |
            (Supplier.last_name.ilike(search_pattern)) |
            (Supplier.company.ilike(search_pattern)) |
            (Supplier.manual_id.ilike(search_pattern)) |
            (Supplier.cin.ilike(search_pattern))
        )

    suppliers = query.order_by(Supplier.last_name, Supplier.first_name).paginate(page=page, per_page=15) # Example pagination
    return render_template('suppliers/list_suppliers.html', suppliers=suppliers, search_term=search_term)

@supplier_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_supplier():
    """Add a new supplier."""
    form = SupplierForm()
    # Pre-fill facility location based on current user
    if request.method == 'GET':
        form.facility_location.data = current_user.facility_location

    if form.validate_on_submit():
        # Check for uniqueness constraints before creating
        existing_manual_id = Supplier.query.filter_by(manual_id=form.manual_id.data).first()
        existing_cin = Supplier.query.filter_by(cin=form.cin.data).first()
        existing_rfid = Supplier.query.filter_by(rfid_uid=form.rfid_uid.data).first() if form.rfid_uid.data else None

        error = False
        if existing_manual_id:
            flash(f'ID "{form.manual_id.data}" existe déjà.', 'error')
            error = True
        if existing_cin:
            flash(f'CIN "{form.cin.data}" existe déjà.', 'error')
            error = True
        if existing_rfid:
             flash(f'RFID UID "{form.rfid_uid.data}" Déjà attribué.', 'error')
             error = True

        if error:
             return render_template('suppliers/add_supplier.html', form=form, title="Add Supplier")

        picture_filename = None
        if form.picture.data:
             picture_filename = save_picture(form.picture.data)

        new_supplier = Supplier(
            manual_id=form.manual_id.data,
            rfid_uid=form.rfid_uid.data or None, # Ensure None if empty
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            company=form.company.data,
            cin=form.cin.data,
            chef_name=form.chef_name.data or None,
            chef_number=form.chef_number.data or None,
            cnss=form.cnss.data or None,
            facility_location=form.facility_location.data,
            picture_url=picture_filename,
            is_active=form.is_active.data
        )
        db.session.add(new_supplier)
        try:
            db.session.commit()
            flash('Fournisseur ajouté avec succès.', 'success')
            return redirect(url_for('supplier.list_suppliers'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l ajout du Fournisseur: {e}', 'error') # More specific error handling might be needed

    return render_template('suppliers/add_supplier.html', form=form, title="Add Supplier")

@supplier_bp.route('/edit/<int:supplier_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_supplier(supplier_id):
    """Edit an existing supplier."""
    supplier = Supplier.query.get_or_404(supplier_id)
    # Ensure admin can only edit suppliers from their facility
    if supplier.facility_location != current_user.facility_location:
         flash('Vous n avez pas la permission de modifier ce Fournisseur.', 'danger')
         return redirect(url_for('supplier.list_suppliers'))

    form = SupplierForm(obj=supplier) # Populate form with supplier data

    if form.validate_on_submit():
         # Check uniqueness constraints (excluding the current supplier)
        existing_manual_id = Supplier.query.filter(Supplier.manual_id == form.manual_id.data, Supplier.id != supplier_id).first()
        existing_cin = Supplier.query.filter(Supplier.cin == form.cin.data, Supplier.id != supplier_id).first()
        existing_rfid = Supplier.query.filter(Supplier.rfid_uid == form.rfid_uid.data, Supplier.id != supplier_id).first() if form.rfid_uid.data else None

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
            # Re-render form with errors, keeping submitted data
            form.picture.data = None # Avoid re-populating file field
            return render_template('suppliers/edit_supplier.html', form=form, title="Edit Supplier", supplier=supplier)


        # Update supplier fields
        supplier.manual_id = form.manual_id.data
        supplier.rfid_uid = form.rfid_uid.data or None
        supplier.first_name = form.first_name.data
        supplier.last_name = form.last_name.data
        supplier.company = form.company.data
        supplier.cin = form.cin.data
        supplier.chef_name = form.chef_name.data or None
        supplier.chef_number = form.chef_number.data or None
        supplier.cnss = form.cnss.data or None
        supplier.facility_location = form.facility_location.data
        supplier.is_active = form.is_active.data

        if form.picture.data:
            # Optionally delete old picture file here if needed
            picture_filename = save_picture(form.picture.data)
            supplier.picture_url = picture_filename

        db.session.commit()
        flash('Fournisseur mis à jour avec succès.', 'success')
        return redirect(url_for('supplier.list_suppliers'))

    # Populate picture_url separately for display if needed (form doesn't retain FileField value on GET)
    current_picture_url = supplier.picture_url

    return render_template('suppliers/edit_supplier.html', form=form, title="Edit Supplier", supplier=supplier, current_picture_url=current_picture_url)


@supplier_bp.route('/delete/<int:supplier_id>', methods=['POST'])
@login_required
@admin_required
def delete_supplier(supplier_id):
    """Delete a supplier."""
    supplier = Supplier.query.get_or_404(supplier_id)
    # Ensure admin can only delete suppliers from their facility
    if supplier.facility_location != current_user.facility_location:
         flash('Vous n avez pas la permission de supprimer ce fournisseur.', 'danger')
         return redirect(url_for('supplier.list_suppliers'))

    # Optional: Delete associated picture file from filesystem
    # if supplier.picture_url:
    #     try:
    #         picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.basename(supplier.picture_url))
    #         if os.path.exists(picture_path):
    #             os.remove(picture_path)
    #     except Exception as e:
    #         flash(f'Could not delete picture file: {e}', 'warning')

    db.session.delete(supplier)
    db.session.commit()
    flash('Fournisseur supprimé avec succès..', 'success')
    return redirect(url_for('supplier.list_suppliers'))

@supplier_bp.route('/export/csv', methods=['GET'])
@login_required
@admin_required
def export_suppliers_csv():
    """Export all suppliers data to CSV"""
    search_term = request.args.get('search', '')
    
    query = Supplier.query
    
    # Apply filters if search term is provided
    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            (Supplier.first_name.ilike(search_pattern)) |
            (Supplier.last_name.ilike(search_pattern)) |
            (Supplier.company.ilike(search_pattern)) |
            (Supplier.manual_id.ilike(search_pattern)) |
            (Supplier.cin.ilike(search_pattern))
        )
    
    # Get all results (no pagination)
    suppliers = query.all()
    
    return export_model_to_csv(suppliers, 'suppliers')

@supplier_bp.route('/export/excel', methods=['GET'])
@login_required
@admin_required
def export_suppliers_excel():
    """Export all suppliers data to Excel"""
    search_term = request.args.get('search', '')
    
    query = Supplier.query
    
    # Apply filters if search term is provided
    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            (Supplier.first_name.ilike(search_pattern)) |
            (Supplier.last_name.ilike(search_pattern)) |
            (Supplier.company.ilike(search_pattern)) |
            (Supplier.manual_id.ilike(search_pattern)) |
            (Supplier.cin.ilike(search_pattern))
        )
    
    # Get all results (no pagination)
    suppliers = query.all()
    
    return export_model_to_excel(suppliers, 'suppliers')


@supplier_bp.route('/<int:supplier_id>', methods=['GET'])
@login_required
@admin_required
def view_supplier(supplier_id):
    """View details of a specific supplier."""
    supplier = Supplier.query.get_or_404(supplier_id)
    

    attendance_history = SupplierAttendance.query\
        .filter_by(cin=supplier.cin)\
        .order_by(SupplierAttendance.entry_time.desc())\
        .all()
    
    return render_template('suppliers/view_supplier.html', 
                           supplier=supplier, 
                           attendance_history=attendance_history)