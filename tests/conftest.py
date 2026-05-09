# tests/conftest.py
import pytest
from app import create_app, db as _db # Use _db to avoid conflict with db fixture from pytest- SQLAlchemy

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for the test session."""
    _app = create_app(config_name='testing') # Use the 'testing' config
    with _app.app_context():
        yield _app

@pytest.fixture(scope='session')
def db(app):
    """Session-wide test database."""
    # The app context is already active from the 'app' fixture
    _db.create_all() # Create tables based on models
    yield _db
    _db.session.remove()
    _db.drop_all()   # Clean up database after test session

@pytest.fixture(scope='function')
def client(app):
    """A test client for the app (function scope for test isolation)."""
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture(scope='function', autouse=True)
def db_session(db):
    """
    Ensures each test runs in its own transaction, which is rolled back.
    This provides test isolation for database operations.
    """
    connection = db.engine.connect()
    transaction = connection.begin()
    db.session.begin_nested()

    yield db.session # Provide the session to the test

    db.session.rollback() # Rollback the outer transaction
    transaction.rollback()
    connection.close()