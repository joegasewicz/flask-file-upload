from flask import Flask

from flask_file_upload.file_upload import FileUpload
from tests.fixtures.models import mock_blog_model
from tests.fixtures.app import create_app, flask_app


class TestFileUploads:

    def test_init_app(self, create_app, mock_blog_model, flask_app):

        file_upload = FileUpload()
        file_upload.init_app(flask_app)
        assert isinstance(file_upload.app, Flask)

    def test_int_from_str(self):
        file_uploads = FileUpload()

        assert file_uploads.int_from_str("test") == "test_1"
        assert file_uploads.int_from_str("test_2") == "test_3"
        assert file_uploads.int_from_str("test_34") == "test_35"
        assert file_uploads.int_from_str("test_346") == "test_347"

    # def test_save_files(self, create_app):
    #     rv = create_app.post("/blog")
    #     assert "200" in rv.status



