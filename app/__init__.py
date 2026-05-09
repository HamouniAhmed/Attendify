# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os
from app.config import config
from datetime import datetime
from flask_wtf.csrf import CSRFProtect

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()  # Initialize CSRF protection



def create_app(config_name='default'):
    app = Flask(__name__, instance_relative_config=True)
    
    # Load the default configuration
    app.config.from_object(config[config_name])
    # Ensure INSTANCE_DIR for database exists (defined in config.py)
    if not os.path.exists(app.config['INSTANCE_DIR']):
        os.makedirs(app.config['INSTANCE_DIR'], exist_ok=True)
        print(f"Created instance directory: {app.config['INSTANCE_DIR']}")

    # Ensure UPLOAD_FOLDER for user uploads exists (defined in config.py)
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        print(f"Created upload directory: {app.config['UPLOAD_FOLDER']}")
    # Load the instance config, if it exists
    try:
        app.config.from_pyfile('config.py')
    except FileNotFoundError:
        pass
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)  # Enable CSRF protection for the app
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    with app.app_context():
        try:
            # Create all tables if they don't exist yet.
            db.create_all()
            print("✓ Database tables created/verified")

            from app.models import User
            
            # Admin credentials from environment or defaults
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@attendify.com')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            
            # Check if admin exists
            admin = User.query.filter_by(email=admin_email).first()
            if admin:
                # Admin exists but might be soft-deleted - reactivate it
                if not admin.is_active:
                    admin.is_active = True
                    db.session.commit()
                    print(f"✓ Admin reactivated: {admin.email}")
                else:
                    print(f"✓ Admin exists and is active: {admin.email}")
            else:
                # Create new admin
                print("Admin not found, creating...")
                admin_user = User(
                    email=admin_email,
                    role="admin",
                    facility_location="Site 1"
                )
                admin_user.set_password(admin_password)
                admin_user.is_active = True
                db.session.add(admin_user)
                db.session.commit()
                print(f"✓ Admin user created: {admin_email}")
                
        except Exception as e:
            print(f"ERROR creating/reactivating admin: {e}")
            import traceback
            traceback.print_exc()

    from app.models import User, Supplier, Intern, SupplierAttendance, InternAttendance, VisitorAttendance
    
    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.supplier_routes import supplier_bp # <-- Import new blueprint
    from app.routes.intern_routes import intern_bp
    from app.routes.attendance_routes import attendance_bp
    from app.routes.records import records_bp
    from app.routes.dashboard import dashboard
    
    app.register_blueprint(dashboard)
    app.register_blueprint(auth_bp)
    app.register_blueprint(supplier_bp) # <-- Register new blueprint
    app.register_blueprint(intern_bp)   
    app.register_blueprint(attendance_bp)
    app.register_blueprint(records_bp)



    @app.template_filter('dict_update')
    def dict_update(d, other):
        """Update a dictionary with another dictionary and return the result"""
        if not isinstance(d, dict) or not isinstance(other, dict):
            return d
        result = d.copy()
        result.update(other)
        return result




    @app.context_processor
    def inject_datetime():
        return {'datetime': datetime}


      
    return app