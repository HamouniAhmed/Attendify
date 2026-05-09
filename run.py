# run.py
from app import create_app, db

# Creates app with 'default' config from app/__init__.py, which points to DevelopmentConfig
app = create_app(config_name='development') 

if __name__ == '__main__':
    # For development, Flask-Migrate should handle table creation.
    # You might run `flask db upgrade` from the command line.
    # The db.create_all() here can be kept for convenience in simple dev setups
    # but ensure it doesn't conflict with migrations.
    # For a fresh setup without migrations, this is fine.
    with app.app_context():
        # db.create_all() # Consider removing if using Flask-Migrate exclusively
        pass # Migrations will handle DB schema.

    app.run(debug=True) # Debug will be True due to DevelopmentConfig