from flask import Flask

from flask_file_upload.file_uploads import FileUploads


class TestFileUploads:

    app = Flask(__name__)

    def test_init_app(self):

        file_uploads = FileUploads()
        file_uploads.init_app(self.app)
        assert isinstance(file_uploads.app, Flask)



