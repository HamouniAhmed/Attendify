from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from app.controllers.auth import login_user, admin_required
from app.models.user import User
from app import db
from flask_login import login_required, current_user, logout_user
from app.forms.auth_forms import LoginForm,  UserForm, CSRFOnlyForm



auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route
    """
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        success, user = login_user(email, password)
        if success:
            next_page = request.args.get('next')
            return redirect(next_page or (url_for('dashboard.admin_dashboard') if user.role == 'admin' else url_for('attendance.attendance_home')))
        else:
            flash("Adresse e-mail ou mot de passe invalide.", "danger")
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
def logout():
    """
    User logout route
    """
    logout_user()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for('auth.login'))


@auth_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def list_users():
    """
    List all users (admin only)
    """
    users = User.query.all()
    form =CSRFOnlyForm()
    return render_template('auth/users.html', users=users, form=form)

@auth_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """
    Add new user (admin only)
    """
    form = UserForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("L'utilisateur existe déjà.", "error")        
        else:
            new_user = User(
                email=form.email.data,
                role=form.role.data,
                facility_location=form.facility_location.data
            )
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash("Utilisateur créé avec succès.", "success")

            return redirect(url_for('auth.list_users'))
    
    return render_template('auth/add_user.html', form=form)

@auth_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("Utilisateur supprimé avec succès.", "success")
    return redirect(url_for('auth.list_users'))

