from flask import Blueprint, render_template, jsonify, redirect, url_for, request
from flask_login import login_required, current_user
from app.models.supplier import Supplier
from app.models.intern import Intern
from app.models.attendance import SupplierAttendance, InternAttendance, VisitorAttendance
from sqlalchemy import func, desc
import pandas as pd
import json
from datetime import datetime, timedelta

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/')
@login_required
def index():
    """Redirection vers le tableau de bord"""
    if current_user.role == 'admin':
        return redirect(url_for('dashboard.admin_dashboard'))
    else:
        return redirect(url_for('attendance.attendance_home'))

@dashboard.route('/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard main view"""
    if current_user.role != 'admin':
        return render_template('errors/403.html'), 403
    
    # Cette route rend simplement le template - les données sont chargées via AJAX
    return render_template('admin/dashboard.html')

@dashboard.route('/api/dashboard/summary')
@login_required
def get_dashboard_summary():
    """API route pour récupérer les données de résumé du tableau de bord"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    # Compte des fournisseurs et stagiaires actifs
    active_suppliers = Supplier.query.filter_by(is_active=True).count()
    active_interns = Intern.query.filter_by(is_active=True).count()
    
    # Présences actuelles (aujourd'hui, pas encore sorti)
    today = datetime.now().date()
    current_suppliers = SupplierAttendance.query.filter(
        func.date(SupplierAttendance.entry_time) == today,
        SupplierAttendance.exit_time.is_(None)
    ).count()
    
    current_interns = InternAttendance.query.filter(
        func.date(InternAttendance.entry_time) == today,
        InternAttendance.exit_time.is_(None)
    ).count()
    
    current_visitors = VisitorAttendance.query.filter(
        func.date(VisitorAttendance.entry_time) == today,
        VisitorAttendance.exit_time.is_(None)
    ).count()
    
    # Total des présences aujourd'hui
    total_suppliers_today = SupplierAttendance.query.filter(
        func.date(SupplierAttendance.entry_time) == today
    ).count()
    
    total_interns_today = InternAttendance.query.filter(
        func.date(InternAttendance.entry_time) == today
    ).count()
    
    total_visitors_today = VisitorAttendance.query.filter(
        func.date(VisitorAttendance.entry_time) == today
    ).count()
    
    return jsonify({
        'active_suppliers': active_suppliers,
        'active_interns': active_interns,
        'current_suppliers': current_suppliers,
        'current_interns': current_interns,
        'current_visitors': current_visitors,
        'total_suppliers_today': total_suppliers_today,
        'total_interns_today': total_interns_today,
        'total_visitors_today': total_visitors_today
    })

@dashboard.route('/api/dashboard/top-suppliers')
@login_required
def get_top_suppliers():
    """API route pour récupérer les 10 meilleures entreprises de fournisseurs en termes d'heures passées"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    last_month = datetime.now() - timedelta(days=30)
    
    # Agréger les heures par entreprise (company)
    top_companies_data = SupplierAttendance.query.with_entities(
        SupplierAttendance.company,
        func.sum(func.coalesce(SupplierAttendance.hours_spent, 0)).label('total_hours')
    ).filter(
        SupplierAttendance.entry_time >= last_month
    ).group_by(
        SupplierAttendance.company
    ).order_by(
        desc('total_hours')
    ).limit(10).all()

    if not top_companies_data:
        top_companies_data = SupplierAttendance.query.with_entities(
            SupplierAttendance.company,
            func.sum(func.coalesce(SupplierAttendance.hours_spent, 0)).label('total_hours')
        ).group_by(
            SupplierAttendance.company
        ).order_by(
            desc('total_hours')
        ).limit(10).all()
    
    result = [
        {
            'company': company_data.company,
            'hours': round(company_data.total_hours, 2) if company_data.total_hours is not None else 0
        }
        for company_data in top_companies_data
    ]
    
    return jsonify(result)

@dashboard.route('/api/dashboard/attendance-by-location')
@login_required
def get_attendance_by_location():
    """API route pour récupérer les données de présence par site"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    # Période des 30 derniers jours
    last_month = datetime.now() - timedelta(days=30)
    
    # Compter les présences des fournisseurs par site
    supplier_counts = SupplierAttendance.query.with_entities(
        SupplierAttendance.facility_location,
        func.count(SupplierAttendance.id).label('count')
    ).filter(
        SupplierAttendance.entry_time >= last_month
    ).group_by(
        SupplierAttendance.facility_location
    ).all()
    
    # Compter les présences des stagiaires par site
    intern_counts = InternAttendance.query.with_entities(
        InternAttendance.facility_location,
        func.count(InternAttendance.id).label('count')
    ).filter(
        InternAttendance.entry_time >= last_month
    ).group_by(
        InternAttendance.facility_location
    ).all()
    
    # Préparer les données pour le graphique
    locations = set()
    for item in supplier_counts:
        locations.add(item.facility_location)
    for item in intern_counts:
        locations.add(item.facility_location)
    
    results = []
    for location in locations:
        supplier_count = next((item.count for item in supplier_counts if item.facility_location == location), 0)
        intern_count = next((item.count for item in intern_counts if item.facility_location == location), 0)
        
        results.append({
            'location': location,
            'suppliers': supplier_count,
            'interns': intern_count
        })
    
    return jsonify(results)

@dashboard.route('/api/dashboard/attendance-trend')
@login_required
def get_attendance_trend():
    """API route pour récupérer les tendances de présence sur les 14 derniers jours"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès non autorisé'}), 403
    
# Période des 30 derniers jours
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=29)  # 30 jours au total

    # Préparer une liste de toutes les dates de la période
    date_range = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]
    
    # Compter les présences des fournisseurs par jour
    supplier_trend = SupplierAttendance.query.with_entities(
        func.date(SupplierAttendance.entry_time).label('date'),
        func.count(SupplierAttendance.id).label('count')
    ).filter(
        func.date(SupplierAttendance.entry_time) >= start_date,
        func.date(SupplierAttendance.entry_time) <= end_date
    ).group_by(
        func.date(SupplierAttendance.entry_time)
    ).all()
    
    # Compter les présences des stagiaires par jour
    intern_trend = InternAttendance.query.with_entities(
        func.date(InternAttendance.entry_time).label('date'),
        func.count(InternAttendance.id).label('count')
    ).filter(
        func.date(InternAttendance.entry_time) >= start_date,
        func.date(InternAttendance.entry_time) <= end_date
    ).group_by(
        func.date(InternAttendance.entry_time)
    ).all()
    
    # Compter les présences des visiteurs par jour
    visitor_trend = VisitorAttendance.query.with_entities(
        func.date(VisitorAttendance.entry_time).label('date'),
        func.count(VisitorAttendance.id).label('count')
    ).filter(
        func.date(VisitorAttendance.entry_time) >= start_date,
        func.date(VisitorAttendance.entry_time) <= end_date
    ).group_by(
        func.date(VisitorAttendance.entry_time)
    ).all()
    
    # Convertir à un format compatible pour le graphique
    supplier_data = {str(item.date): item.count for item in supplier_trend}
    intern_data = {str(item.date): item.count for item in intern_trend}
    visitor_data = {str(item.date): item.count for item in visitor_trend}
    
    result = []
    for date_str in date_range:
        result.append({
            'date': date_str,
            'suppliers': supplier_data.get(date_str, 0),
            'interns': intern_data.get(date_str, 0),
            'visitors': visitor_data.get(date_str, 0)
        })
    
    return jsonify(result)

@dashboard.route('/api/dashboard/interns-by-department')
@login_required
def get_interns_by_department():
    """API route pour récupérer la répartition des stagiaires par département"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    # Compter les stagiaires actifs par département
    interns_by_dept = Intern.query.with_entities(
        Intern.department,
        func.count(Intern.id).label('count')
    ).filter(
        Intern.is_active == True
    ).group_by(
        Intern.department
    ).all()
    
    result = [
        {
            'department': item.department,
            'count': item.count
        }
        for item in interns_by_dept
    ]
    
    return jsonify(result)

@dashboard.route('/api/dashboard/interns-by-type')
@login_required
def get_interns_by_type():
    """API route pour récupérer la répartition des stagiaires par type"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    # Compter les stagiaires actifs par type
    interns_by_type = Intern.query.with_entities(
        Intern.intern_type,
        func.count(Intern.id).label('count')
    ).filter(
        Intern.is_active == True
    ).group_by(
        Intern.intern_type
    ).all()
    
    result = [
        {
            'type': item.intern_type,
            'count': item.count
        }
        for item in interns_by_type
    ]
    
    return jsonify(result)

@dashboard.route('/api/dashboard/suppliers-by-type')
@login_required
def get_suppliers_by_type():
    """API route pour récupérer la répartition des fournisseurs par type (visite vs intervention)"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    # Période des 30 derniers jours
    last_month = datetime.now() - timedelta(days=30)
    
    # Compter les fournisseurs par type de présence
    suppliers_by_type = SupplierAttendance.query.with_entities(
        SupplierAttendance.presence_type,
        func.count(SupplierAttendance.id).label('count')
    ).filter(
        SupplierAttendance.entry_time >= last_month
    ).group_by(
        SupplierAttendance.presence_type
    ).all()

    if not suppliers_by_type:
        suppliers_by_type = SupplierAttendance.query.with_entities(
            SupplierAttendance.presence_type,
            func.count(SupplierAttendance.id).label('count')
        ).group_by(
            SupplierAttendance.presence_type
        ).all()
    
    result = [
        {
            'type': item.presence_type,
            'count': item.count
        }
        for item in suppliers_by_type
    ]
    
    return jsonify(result)
@dashboard.route('/api/dashboard/suppliers-by-company')
@login_required
def get_suppliers_by_company():
    """API route pour récupérer la répartition des fournisseurs par entreprise"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    # Période des 30 derniers jours
    last_month = datetime.now() - timedelta(days=30)
    
    # Compter les fournisseurs par entreprise
    suppliers_by_company = SupplierAttendance.query.with_entities(
        SupplierAttendance.company,
        func.count(SupplierAttendance.id).label('count')
    ).filter(
        SupplierAttendance.entry_time >= last_month
    ).group_by(
        SupplierAttendance.company
    ).order_by(
        desc('count')
    ).limit(10).all()  # Limiter aux 10 entreprises les plus fréquentes

    if not suppliers_by_company:
        suppliers_by_company = SupplierAttendance.query.with_entities(
            SupplierAttendance.company,
            func.count(SupplierAttendance.id).label('count')
        ).group_by(
            SupplierAttendance.company
        ).order_by(
            desc('count')
        ).limit(10).all()
    
    result = [
        {
            'company': item.company if item.company else 'Non spécifié',
            'count': item.count
        }
        for item in suppliers_by_company
    ]
    
    return jsonify(result)