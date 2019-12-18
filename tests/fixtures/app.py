import pytest
from flask import Flask, request
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
db = SQLAlchemy()


@app.route("/config_test", methods=["POST"])
def config_test():
    from ..fixtures.models import mock_blog_model

    file = request.files["file"]

    config = Config()
    config.init_config(app)

    file_util = FileUtils(mock_blog_model, config, table_name="blogs")
    file_util.save_file(file, 1)

    return {
        "data": "hello"
    }, 200


@app.route("/blog", methods=["GET", "POST"])
def blog():
    from .models import MockBlogModel
    if request.method == "GET":
        pass
    if request.method == "POST":

        my_video = request.files["my_video"]
        placeholder_img = request.files["my_placeholder"]
        print("arrived here ------>? ")
        blog_post = MockBlogModel(name="My Blog Post")

        file_upload = FileUpload()

        blog = file_upload.save_files(blog_post, files={
            "my_video": my_video,
            "placeholder_img": placeholder_img,
        })

        db.session.add(blog)
        db.session.commit()

        blog_post = MockBlogModel()
        blog_data = blog_post.get_blog()

        return {
            "blog": f"{blog_data}"
        }, 200


@pytest.fixture
def flask_app():
    db.init_app(app)
    return app


@pytest.fixture
def create_app():
    db.init_app(app)
    testing_client = app.test_client()

    ctx = app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()
