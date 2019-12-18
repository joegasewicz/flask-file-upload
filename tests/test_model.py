
from flask_file_upload.file_upload import FileUpload
from tests.fixtures.app import db
from flask_file_upload.model import Model


class TestModel:

    test_results = {
        "my_video__file_name": "video1",
        "my_video__mime_type": "video/mpeg",
        "my_video__file_type": "mp4",
        "my_placeholder__file_name": "placeholder1",
        "my_placeholder__mime_type": "image/jpeg",
        "my_placeholder__file_type": "jpg",
        "id": 1,
    }

    def test_model(self):

        file_upload = FileUpload()

        @file_upload.Model
        class ModelTest(db.Model):
            __tablename__ = "tests"
            id = db.Column(db.Integer, primary_key=True)
            my_placeholder = file_upload.Column(db)
            my_video = file_upload.Column(db)

        model_test = ModelTest(**self.test_results)

        assert hasattr(model_test, "my_video__file_name")
        assert hasattr(model_test, "my_video__mime_type")
        assert hasattr(model_test, "my_video__file_type")
        assert not hasattr(model_test, "my_video")
        assert hasattr(model_test, "my_placeholder__file_name")
        assert hasattr(model_test, "my_placeholder__mime_type")
        assert hasattr(model_test, "my_placeholder__file_type")
        assert not hasattr(model_test, "my_placeholder")
        assert hasattr(model_test, "id")

        assert model_test.my_video__file_name == "video1"
        assert model_test.my_video__mime_type == "video/mpeg"
        assert model_test.my_video__file_type == "mp4"
        assert model_test.my_placeholder__file_name == "placeholder1"
        assert model_test.my_placeholder__mime_type == "image/jpeg"
        assert model_test.my_placeholder__file_type == "jpg"
        assert model_test.id == 1

    def test_create_keys(self):
        result = {
            "my_video__file_name": None,
            "my_video__mime_type": None,
            "my_video__file_type": None,
        }

        file_upload = FileUpload()
        assert result == file_upload.Model.create_keys(file_upload.Model.keys, "my_video")
