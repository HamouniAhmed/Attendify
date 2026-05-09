# tests/models/test_user.py
from app.models.user import User # Your User model
# No need to import 'db' here if using the db_session fixture for operations

def test_new_user_creation(db_session): # Uses the db_session fixture
    """
    GIVEN a User model
    WHEN a new User is created and password set
    THEN check the email, role, facility_location, and password hashing
    """
    user = User(email='pytest_user@example.com', role='user', facility_location='Test Facility')
    user.set_password('secure_password123')

    db_session.add(user)
    db_session.commit() # Commit to save the user

    retrieved_user = User.query.filter_by(email='pytest_user@example.com').first()
    assert retrieved_user is not None
    assert retrieved_user.email == 'pytest_user@example.com'
    assert retrieved_user.role == 'user'
    assert retrieved_user.check_password('secure_password123')
    assert not retrieved_user.check_password('wrong_password')
    assert not retrieved_user.is_admin()

def test_admin_user_property(db_session):
    """
    GIVEN a User model
    WHEN a new User with role 'admin' is created
    THEN check the is_admin property returns True
    """
    admin = User(email='pytest_admin@example.com', role='admin', facility_location='Admin HQ')
    admin.set_password('admin_pass')

    db_session.add(admin)
    db_session.commit()

    assert admin.is_admin() is True