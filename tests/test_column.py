from flask_file_upload.file_uploads import FileUploads
from tests.fixtures.app import db


class TestColumn:

    def test_column(self):

        file_uploads = FileUploads()

        @file_uploads.Column("test", db=db)
        class ModelTest:
            pass

        model_test = ModelTest()

        assert hasattr(model_test, "test_file_name")
        assert hasattr(model_test, "test_mime_type")
        assert hasattr(model_test, "test_file_type")

