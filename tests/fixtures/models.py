import pytest

import sqlalchemy

from .app import db
from flask_file_upload.file_uploads import FileUploads

file_uploads = FileUploads()


# @file_uploads.Model("my_video")
class MockBlogModel(db.Model):
    __tablename__ = "blogs"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))

    def get_blog(self):
        return self.query.filter_by(id=1).one()



@pytest.fixture
def mock_blog_model():
    return MockBlogModel
