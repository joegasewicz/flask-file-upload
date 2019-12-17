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
def mock_model():
    class ModelModel:
        my_video__file_name = "video1",
        my_video__mime_type = "video/mpeg",
        my_video__file_type = "mp4",
        my_placeholder__file_name = "placeholder1",
        my_placeholder__mime_type = "image/jpeg",
        my_placeholder__file_type = "jpg",
    return ModelModel


@pytest.fixture
def mock_blog_model():
    return MockBlogModel
