import os
import pytest
from flask import Flask

from flask_file_upload.file_upload import FileUpload
from tests.fixtures.models import mock_blog_model, mock_model
from tests.fixtures.app import create_app, flask_app


class TestFileUploads:

    my_video = os.path.join("tests/assets/my_video.mp4")
    my_placeholder = os.path.join("tests/assets/my_placeholder.png")

    file_data = [
        {
            "my_video__file_name": "video1",
            "my_video__mime_type": "video/mpeg",
            "my_video__file_type": "mp4",
        },
        {
            "my_placeholder__file_name": "placeholder1",
            "my_placeholder__mime_type": "image/jpeg",
            "my_placeholder__file_type": "jpg",
        }
    ]

    def test_init_app(self, create_app, mock_blog_model, flask_app):

        file_upload = FileUpload()
        file_upload.init_app(flask_app)
        assert isinstance(file_upload.app, Flask)

    def test_set_model_attrs(self, mock_model):
        file_upload = FileUpload()
        file_upload.file_data = self.file_data
        file_upload._set_model_attrs(mock_model)
        
        assert hasattr(mock_model, "my_video__file_name")
        assert hasattr(mock_model, "my_video__mime_type")
        assert hasattr(mock_model, "my_video__file_type")
        assert hasattr(mock_model, "my_placeholder__file_name")
        assert hasattr(mock_model, "my_placeholder__mime_type")
        assert hasattr(mock_model, "my_placeholder__file_type")

        assert mock_model.my_video__file_name == "video1"
        assert mock_model.my_video__mime_type == "video/mpeg"
        assert mock_model.my_video__file_type == "mp4"
        assert mock_model.my_placeholder__file_name == "placeholder1"
        assert mock_model.my_placeholder__mime_type == "image/jpeg"
        assert mock_model.my_placeholder__file_type == "jpg"

        with pytest.raises(AttributeError):
            file_upload.file_data[0]["bananas"] = "bananas"
            file_upload._set_model_attrs(mock_model)

    @pytest.mark.j
    def test_save_files(self, create_app):
        data = {
            "my_video": (self.my_video, "my_video.mp4"),
            "my_placeholder": (self.my_placeholder, "my_placeholder.png")
        }
        rv = create_app.post("/blog", data=data, content_type="multipart/form-data")
        assert "200" in rv.status
