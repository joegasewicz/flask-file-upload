import pytest
from werkzeug.datastructures import FileStorage
import io
import json


@pytest.fixture
def video_file():
    mock_file = FileStorage(
        stream=io.BytesIO(b"123456"),
        filename="my_video.mp4",
        content_type="video/mpeg",
    )
    return mock_file


@pytest.fixture
def png_file():
    mock_file = FileStorage(
        stream=io.BytesIO(b"123456"),
        filename="my_png.png",
        content_type="image/png",
    )
    return mock_file
