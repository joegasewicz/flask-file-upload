from flask_file_upload.file_uploads import FileUploads


class TestColumn:

    def test_column(self):

        file_uploads = FileUploads()

        @file_uploads.Column("test")
        class ModelTest:
            pass

        model_test = ModelTest()

        assert model_test.file_name == "test"

