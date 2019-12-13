from flask import Flask


from flask_file_upload._config import Config


class TestConfig:

    app = Flask(__name__)

    app.config["UPLOAD_FOLDER"] = "/test_path"
    app.config["ALLOWED_EXTENSIONS"] = ["jpg", "png", "mov", "mp4", "mpg"]
    app.config["MAX_CONTENT_LENGTH"] = 1000 * 1024 * 1024

    def test_init_config(self):
        config = Config()
        config.init_config(self.app)

        assert config.upload_folder == "/test_path"
        assert config.allowed_extensions == ["jpg", "png", "mov", "mp4", "mpg"]
        assert config.max_content_length == 1048576000