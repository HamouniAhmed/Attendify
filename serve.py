# serve.py
from waitress import serve
from app import create_app, db # Import db as well for potential db.create_all()
import os

# Determine config: use FLASK_CONFIG env var, or default.
# For the supervisor's version launched by launcher.py, FLASK_CONFIG will be set.
config_name = os.getenv('FLASK_CONFIG') or 'development' # Default to development if not set

app = create_app(config_name=config_name)

with app.app_context():
    # This will create DB and tables if they don't exist in instance/attendance.db
    # This is useful for the first run of the packaged app.
    # Flask-Migrate is for schema changes after the initial creation.
    db.create_all()
    print(f"Database tables checked/created at {app.config['SQLALCHEMY_DATABASE_URI']}")

if __name__ == '__main__':
    host = '127.0.0.1' 
    port = 5000
    
    print(f"Starting server with Waitress on http://{host}:{port} using '{config_name}' configuration.")
    serve(app, host=host, port=port, threads=8)