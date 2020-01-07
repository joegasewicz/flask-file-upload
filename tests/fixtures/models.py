import pytest

import sqlalchemy

from tests.app import db, file_upload


@file_upload.Model
class MockBlogModel(db.Model):
    __tablename__ = "blogs"
    __table_args__ = {'extend_existing': True}
    __mapper_args__ = {'always_refresh': True}
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    # File attributes
    my_placeholder = file_upload.Column()
    my_video = file_upload.Column()

    def get_name(self):
        return "joe"

    def get_blog(self):
        return self.query.filter_by(id=1).one()

    @staticmethod
    def get_blog_by_id():
        return 1

class MockModel:
    __tablename__ = "blogs"
    my_video__file_name = "video1"
    my_video__mime_type = "video/mpeg"
    my_video__file_type = "mp4"
    my_placeholder__file_name = "placeholder1"
    my_placeholder__mime_type = "image/jpeg"
    my_placeholder__file_type = "jpg"


@pytest.fixture
def mock_model():
    return MockModel


@pytest.fixture
def mock_blog_model():
    return MockBlogModel
