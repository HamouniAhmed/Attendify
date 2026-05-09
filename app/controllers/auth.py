# app/controllers/auth.py
from flask import  flash, redirect, url_for
from app.models.user import User
from app import db
import functools

from flask_login import login_user as flask_login_user, logout_user as flask_logout_user, current_user

def login_user(email, password):
    """
    Authenticate and login a user
    """
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
        flask_login_user(user)
        return True, user
    
    return False, None

def admin_required(view):
    """
    Decorator to enforce admin role requirement for views
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("Vous n'avez pas la permission d'accéder à cette page.", 'error')
            return redirect(url_for('dashboard.index'))
        return view(**kwargs)
    return wrapped_view

