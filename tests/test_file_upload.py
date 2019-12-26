import os
import pytest
from flask import Flask, current_app
from werkzeug.datastructures import FileStorage
from shutil import copyfile
from flask_sqlalchemy import SQLAlchemy
import time

from flask_file_upload._config import Config
from flask_file_upload.file_upload import FileUpload
from tests.fixtures.models import mock_blog_model, mock_model
from tests.app import create_app, flask_app, db, file_upload, app


class TestFileUploads:

    my_video = os.path.join("tests/assets/my_video.mp4")
    my_video_update = os.path.join("tests/assets/my_video_update.mp4")
    my_placeholder = os.path.join("tests/assets/my_placeholder.png")

    dest_my_video = os.path.join("tests/test_path/blogs/1/my_video.mp4")
    dest_my_video_update = "tests/test_path/blogs/1/my_video_updated.mp4"
    dest_my_placeholder = "tests/test_path/blogs/1/my_placeholder.png"

    attrs = {
        "id": 1,
        "name": "test_name",
        "my_video__file_name": "my_video.mp4",
        "my_video__mime_type": "video/mpeg",
        "my_video__file_type": "mp4",
        "my_placeholder__file_name": "my_placeholder.png",
        "my_placeholder__mime_type": "image/jpeg",
        "my_placeholder__file_type": "jpg",
    }

    file_data = [
        {
            "my_video__file_name": "my_video.mp4",
            "my_video__mime_type": "video/mpeg",
            "my_video__file_type": "mp4",
        },
        {
            "my_placeholder__file_name": "my_placeholder.png",
            "my_placeholder__mime_type": "image/jpeg",
            "my_placeholder__file_type": "jpg",
        }
    ]

    def setup_method(self):
        # Copy files from asset dir to test dir here:
        copyfile("tests/assets/my_video.mp4", "tests/test_path/blogs/1/my_video.mp4")

    def teardown_method(self):
        # Delete the files from the test dir here:
        try:
            pass
            os.remove("tests/test_path/blogs/1/my_video_updated.mp4")
        except:
            pass

    def test_init_app(self, create_app, mock_blog_model, flask_app):

        file_upload = FileUpload()
        file_upload.init_app(flask_app)
        assert isinstance(file_upload.app, Flask)

    def test_set_model_attrs(self, mock_model):
        file_upload = FileUpload()
        file_upload.file_data = self.file_data
        file_upload._set_model_attrs(mock_model)

        assert mock_model.my_video__file_name == "my_video.mp4"
        assert mock_model.my_video__mime_type == "video/mpeg"
        assert mock_model.my_video__file_type == "mp4"
        assert mock_model.my_placeholder__file_name == "my_placeholder.png"
        assert mock_model.my_placeholder__mime_type == "image/jpeg"
        assert mock_model.my_placeholder__file_type == "jpg"

        with pytest.raises(AttributeError):
            file_upload.file_data[0]["bananas"] = "bananas"
            file_upload._set_model_attrs(mock_model)

    def test_save_files(self, create_app):
        data = {
            "my_video": (self.my_video, "my_video.mp4"),
            "my_placeholder": (self.my_placeholder, "my_placeholder.png")
        }
        rv = create_app.post("/blog", data=data, content_type="multipart/form-data")
        assert "200" in rv.status

    def test_stream_file(self, create_app):
        rv = create_app.get("/blog")
        assert "200" in rv.status

    @pytest.mark.d
    def test_update_files(self, create_app, mock_blog_model):
        file_upload.config.upload_folder = "tests/test_path"

        m = mock_blog_model(
            name="hello",
            my_video__file_name="my_video.mp4",
            my_video__mime_type="video/mpeg",
            my_video__file_type="mp4",
        )

        db.session.add(m)
        db.session.commit()

        new_file = FileStorage(
                stream=open(self.my_video_update, "rb"),
                filename="my_video_updated.mp4",
                content_type="video/mpeg",
            )

        blog = m.get_blog()

        file_upload.update_files(
            blog,
            db,
            files={"my_video": new_file},
        )

        # Test files / dirs
        assert "my_video_updated.mp4" in os.listdir("tests/test_path/blogs/1")
        assert "my_video.mp4" not in os.listdir("tests/test_path/blogs/1")


    # @pytest.mark.g
    # def test_update_files_2(self, mock_blog_model):
    #     db.init_app(app)
    #     db.create_all()
    #     file_upload = FileUpload()
    #     file_upload.init_app(app)
    #
    #     new_file = FileStorage(
    #             stream=open(self.my_video_update, "rb"),
    #             filename="my_video_updated.mp4",
    #             content_type="video/mpeg",
    #         )
    #
    #     model = mock_blog_model(**self.attrs)
    #
    #     assert model.my_video__file_name == "my_video.mp4"
    #     assert model.my_video__mime_type == "video/mpeg"
    #     assert model.my_video__file_type == "mp4"
    #
    #     result = file_upload.update_files(
    #         model,
    #         files={"my_video": new_file},
    #     )
    #
    #     assert result.my_video__file_name == "my_video_updated.mp4"
    #     assert result.my_video__mime_type == "mp4"
    #     assert result.my_video__file_type == "video/mpeg"
    #


    def test_delete_files(self):
        pass

    def test_get_file_url(self):
        pass
