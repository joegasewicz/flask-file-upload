from flask import Flask

from flask_file_upload.file_upload import FileUpload
from tests.fixtures.models import mock_blog_model
from tests.fixtures.app import create_app, flask_app


class TestFileUploads:
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

    def test_set_model_attrs(self):
        class MockModel:
            pass
        file_upload = FileUpload()
        file_upload.file_data = self.file_data
        file_upload.set_model_attrs(MockModel)
        
        assert hasattr(MockModel, "my_video__file_name")
        assert hasattr(MockModel, "my_video__mime_type")
        assert hasattr(MockModel, "my_video__file_type")
        assert hasattr(MockModel, "my_placeholder__file_name")
        assert hasattr(MockModel, "my_placeholder__mime_type")
        assert hasattr(MockModel, "my_placeholder__file_type")

        assert MockModel.my_video__file_name == "video1"
        assert MockModel.my_video__mime_type == "video/mpeg"
        assert MockModel.my_video__file_type == "mp4"
        assert MockModel.my_placeholder__file_name == "placeholder1"
        assert MockModel.my_placeholder__mime_type == "image/jpeg"
        assert MockModel.my_placeholder__file_type == "jpg"

    # def test_save_files(self, create_app):
    #     rv = create_app.post("/blog")
    #     assert "200" in rv.status

