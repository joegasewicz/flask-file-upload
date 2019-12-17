import pytest

import sqlalchemy

from .app import db
from flask_file_upload.file_upload import FileUpload

file_upload = FileUpload()


@file_upload.Model
class MockBlogModel(db.Model):
    __tablename__ = "blogs"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    my_placeholder = file_upload.Column(db)
    my_video = file_upload.Column(db)

    def get_blog(self):
        return self.query.filter_by(id=1).one()



@pytest.fixture
def mock_blog_model():
    return MockBlogModel
