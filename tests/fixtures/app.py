import pytest
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

from flask_file_upload.file_upload import FileUpload

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
db = SQLAlchemy()


@app.route("/blog", methods=["GET", "POST"])
def blog():
    from .models import MockBlogModel
    if request.method == "GET":
        pass
    if request.method == "POST":
        my_video = request.files["my_video"]
        placeholder_img = request.files["placeholder_img"]
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
    app.config["UPLOAD_FOLDER"] = "/test_path"
    app.config["ALLOWED_EXTENSIONS"] = ["jpg", "png", "mov", "mp4", "mpg"]
    app.config["MAX_CONTENT_LENGTH"] = 1000 * 1024 * 1024
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
