import pytest
from sqlalchemy import Column, String

from flask_file_upload._model_utils import _ModelUtils
from tests.fixtures.models import MockModel


class Test_ModelUtils:

    def test_create_keys(self):
        model_data = {
            "my_video__file_name": Column(String, key="my_video__file_name", name="my_video__file_name"),
            "my_video__mime_type": Column(String, key="my_video__mime_type", name="my_video__mime_type"),
            "my_video__file_type": Column(String, key="my_video__file_type", name="my_video__file_type"),
        }

        results = _ModelUtils.create_keys(
            _ModelUtils.keys,
            "my_video",
            lambda key, name: Column(String, key=key, name=name)
        )

        assert str(results["my_video__file_name"]) == str(model_data["my_video__file_name"])
        assert str(results["my_video__mime_type"]) == str(model_data["my_video__mime_type"])
        assert str(results["my_video__file_type"]) == str(model_data["my_video__file_type"])

    @pytest.mark.t
    def test_get_by_postfix(self):
        # TODO remove 'in' from assertion

        assert "mp4" in _ModelUtils.get_by_postfix(MockModel, "my_video", _ModelUtils.keys[1])
