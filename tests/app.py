import pytest
from flask import Flask, request, send_from_directory, current_app
from flask_sqlalchemy import SQLAlchemy

from flask_file_upload.file_upload import FileUpload
from flask_file_upload.file_utils import FileUtils
from flask_file_upload._config import Config

app = Flask(__name__)
app.config["SERVERNAME"] = "127.0.0.1:5000"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
app.config["UPLOAD_FOLDER"] = "tests/test_path"
app.config["ALLOWED_EXTENSIONS"] = ["jpg", "png", "mov", "mp4", "mpg"]
app.config["MAX_CONTENT_LENGTH"] = 1000 * 1024 * 1024
db = SQLAlchemy(app)
file_upload = FileUpload(app, db)


@app.route("/config_test", methods=["POST"])
def config_test():
    from tests.fixtures.models import MockBlogModel

    file = request.files["file"]
    current_app.config["UPLOAD_FOLDER"] = "tests/test_path"
    config = Config()
    config.init_config(app)

    file_util = FileUtils(MockBlogModel(name="test_save"), config)
    file_util.save_file(file, 1)

    return {
        "data": "hello"
    }, 200

@app.route("/blogs", methods=["GET"])
def blogs():
    from tests.fixtures.models import MockBlogModel

    blogs = MockBlogModel.get_all_blogs()

    results = file_upload.add_file_urls_to_models(blogs, filename="my_video", backref={
        "name": "news",
        "filename": "news_image",
    })

    # assert results == []


    return {
        "results": {
            "my_video_url": results[0].my_video_url,
            "my_video_url_2": results[1].my_video_url,
            "news_image_url": results[0].news[0].news_image_url,
            # "news_video_url": results[0].news[0].news_video_url,
            "news_image_url_2": results[0].news[1].news_image_url,
            # "news_video_url_url": results[0].news[1].news_video_url,
        },
    }, 200


@app.route("/blog", methods=["GET", "POST"])
def blog():
    from tests.fixtures.models import MockBlogModel
    if request.method == "GET":

        blog_post = MockBlogModel(
            id=1,
            name="My Blog Post",
            my_video__file_name="my_video.mp4",
            my_video__mime_type="video/mpeg",
            my_video__file_type="mp4",
        )
        file_upload = FileUpload(app, db)
        # Warning - The UPLOAD_FOLDER - only needs to be reset for testing!
        current_app.config["UPLOAD_FOLDER"] = "test_path"
        file_upload.init_app(app, db)
        return file_upload.stream_file(blog_post, filename="my_video")

    if request.method == "POST":

        my_video = request.files["my_video"]
        my_placeholder = request.files["my_placeholder"]

        blog_post = MockBlogModel(id=2, name="My Blog Post")

        file_upload = FileUpload(app, db)

        blog = file_upload.save_files(blog_post, files={
            "my_video": my_video,
            "my_placeholder": my_placeholder,
        })


        blog_post = MockBlogModel()
        blog_data = blog_post.get_blog()

        return {
            "blog": f"{blog_data}"
        }, 200


@pytest.fixture
def flask_app():
    from tests.fixtures.models import mock_blog_model
    db.init_app(app)
    db.create_all()
    return app


@pytest.fixture
def create_app():
    from tests.fixtures.models import MockBlogModel, MockModel

    app.config["UPLOAD_FOLDER"] = "tests/test_path"
    file_upload.init_app(app, db)

    with app.app_context():

        db.create_all()

    testing_client = app.test_client()

    ctx = app.app_context()
    ctx.push()

    yield testing_client

    with app.app_context():
        db.session.remove()
        db.drop_all()

    ctx.pop()
