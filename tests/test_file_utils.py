import os
from flask import request

from flask_file_upload.file_utils import FileUtils
from .fixtures.models import mock_blog_model
from .fixtures.config import test_config
from .fixtures.app import create_app


class TestFileUtils:

    file = os.path.join("tests/assets/my_video.mp4")

    def test_save_file(self, create_app):

        rv = create_app.post("/config_test", data={"file": (self.file, "my_video.mp4")}, content_type='multipart/form-data')

        assert "200" in str(rv.status)