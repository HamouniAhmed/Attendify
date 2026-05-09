# tests/routes/test_auth_routes.py
from flask import url_for

def test_login_page_loads(client):
    """
    GIVEN a Flask application client
    WHEN the '/login' page is requested (GET)
    THEN check the response is valid (200) and contains expected text
    """
    response = client.get(url_for('auth.login')) # 'auth' is your blueprint name
    assert response.status_code == 200
    assert b"Connexion" in response.data # Text from your login button or page title
    assert b"Nom d'utilisateur" in response.data # Assuming your form has an 'Email' label or placeholder
    assert b"Mot de passe" in response.data # This one should still be correct based on your HTML
                                  # You might need to adjust this based on your actual login.html

# You would add more tests here:
# - test_successful_login (requires creating a user in db_session first)
# - test_failed_login_wrong_password
# - test_failed_login_unknown_user
# - test_logout