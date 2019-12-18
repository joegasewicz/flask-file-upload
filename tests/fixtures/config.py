import pytest

from flask_file_upload._config import Config

from tests.fixtures.app import app


@pytest.fixture
def test_config():
    return Config().init_config(app)
