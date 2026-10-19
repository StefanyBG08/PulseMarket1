from app import create_app
from app.extensions import db

class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_CLIENT_ID = ""
    GOOGLE_CLIENT_SECRET = ""
    GITHUB_CLIENT_ID = ""
    GITHUB_CLIENT_SECRET = ""
    BASE_URL = "http://localhost"

def test_dashboard_redirects_when_logged_out():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
    client = app.test_client()
    response = client.get("/dashboard")
    assert response.status_code in (302, 401)
    with app.app_context():
        db.drop_all()
