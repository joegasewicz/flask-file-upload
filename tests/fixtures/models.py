import pytest

import sqlalchemy

from tests.app import db, file_upload


@file_upload.Model
class NewsModel(db.Model):
    __tablename__ = "news"
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(100))
    blog_id = db.Column(db.Integer, db.ForeignKey("blogs.id"))

    news_image = file_upload.Column()
    news_video = file_upload.Column()


@file_upload.Model
class MockBlogModel(db.Model):
    __tablename__ = "blogs"
    __table_args__ = {'extend_existing': True}
    __mapper_args__ = {'always_refresh': True}
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    # Relationships
    news = db.relationship(NewsModel, backref="news")
    # File attributes
    my_placeholder = file_upload.Column()
    my_video = file_upload.Column()


    def get_name(self):
        return "joe"

    def get_blog(self, id=1):
        return self.query.filter_by(id=id).one()

    @staticmethod
    def get_all_blogs(id=1):
        return MockBlogModel.query.all()

    @staticmethod
    def get_blog_by_id():
        return 1

class MockModel:
    __tablename__ = "blogs"
    my_video__file_name = "video1"
    my_video__mime_type = "video/mpeg"
    my_video__ext = "mp4"
    my_placeholder__file_name = "placeholder1"
    my_placeholder__mime_type = "image/jpeg"
    my_placeholder__ext = "jpg"


@pytest.fixture
def mock_model():
    return MockModel

@pytest.fixture
def mock_news_model():
    return NewsModel


@pytest.fixture
def mock_blog_model():
    return MockBlogModel

