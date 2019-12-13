from flask import Flask

from flask_file_upload.file_uploads import FileUploads
from tests.fixtures.models import mock_blog_model
from tests.fixtures.app import create_app, app


class TestFileUploads:


    def test_init_app(self, create_app, mock_blog_model):

        file_uploads = FileUploads()
        file_uploads.init_app(app)
        assert isinstance(file_uploads.app, Flask)



