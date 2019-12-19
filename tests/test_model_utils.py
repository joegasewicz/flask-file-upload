import pytest

from flask_file_upload._model_utils import _ModelUtils
from tests.fixtures.models import MockModel


class Test_ModelUtils:

    def test_create_keys(self):
        result = {
            "my_video__file_name": None,
            "my_video__mime_type": None,
            "my_video__file_type": None,
        }

        assert result == _ModelUtils.create_keys(_ModelUtils.keys, "my_video")

    def test_get_by_postfix(self):
        # TODO remove 'in' from assertion

        assert "mp4" in _ModelUtils.get_by_postfix(MockModel, "my_video", _ModelUtils.keys[1])
