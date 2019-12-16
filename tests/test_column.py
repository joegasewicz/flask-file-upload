from flask_file_upload.file_uploads import FileUploads
from tests.fixtures.app import db


class TestColumn:

    def test_column(self):

        file_uploads = FileUploads()

        @file_uploads.Model
        class ModelTest(db.Model):
            __tablename__ = "tests"
            id = db.Column(db.Integer, primary_key=True)
            my_placeholder = file_uploads.Column(db)
            my_video = file_uploads.Column(db)

        model_test = ModelTest()

        assert hasattr(model_test, "my_video_file_name")
        assert hasattr(model_test, "my_video_mime_type")
        assert hasattr(model_test, "my_video_file_type")
        assert not hasattr(model_test, "my_video")
        assert hasattr(model_test, "my_placeholder_file_name")
        assert hasattr(model_test, "my_placeholder_mime_type")
        assert hasattr(model_test, "my_placeholder_file_type")
        assert not hasattr(model_test, "my_placeholder")



