import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
db = SQLAlchemy()


@pytest.fixture
def create_app():
    db.init_app(app)
    testing_client = app.test_client()

    ctx = app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()
