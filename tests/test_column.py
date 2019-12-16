from flask_file_upload.file_upload import FileUpload
from tests.fixtures.app import db


class TestColumn:

    def test_column(self):

        file_upload = FileUpload()

        @file_upload.Model
        class ModelTest(db.Model):
            __tablename__ = "tests"
            id = db.Column(db.Integer, primary_key=True)
            my_placeholder = file_upload.Column(db)
            my_video = file_upload.Column(db)

        model_test = ModelTest()

        assert hasattr(model_test, "my_video_file_name")
        assert hasattr(model_test, "my_video_mime_type")
        assert hasattr(model_test, "my_video_file_type")
        assert not hasattr(model_test, "my_video")
        assert hasattr(model_test, "my_placeholder_file_name")
        assert hasattr(model_test, "my_placeholder_mime_type")
        assert hasattr(model_test, "my_placeholder_file_type")
        assert not hasattr(model_test, "my_placeholder")



