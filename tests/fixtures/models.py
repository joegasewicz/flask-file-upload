import pytest

from .app import db


@pytest.fixture
def mock_blog_model():
    class MockModel(db.Model):
        __tablename__ = "blogs"
        id = db.Column(db.Integer(), primary_key=True)
        name = db.Column(db.String(100))

    return MockModel
