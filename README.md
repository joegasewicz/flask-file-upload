[![Documentation Status](https://readthedocs.org/projects/flask-file-upload/badge/?version=latest)](https://flask-file-upload.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/flask-file-upload.svg)](https://badge.fury.io/py/flask-file-upload)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/flask-file-upload)
![PyPI - License](https://img.shields.io/pypi/l/flask-file-upload?color=yellow)

![FlaskFileUpload](assets/logo.png?raw=true "Title")

Library that works with Flask & SqlAlchemy to store
files on your server & in your database

Read the docs: [Documentation](https://flask-file-upload.readthedocs.io/en/latest/)

## Installation

```bash
pip install flask-file-upload
```

Flask File Upload


##### General Flask config options
````python
    # Important: The below configuration variables need to be set  before
    # initiating `FileUpload`
    UPLOAD_FOLDER = join(dirname(realpath(__file__)), "uploads/media")
    ALLOWED_EXTENSIONS = ["jpg", "png", "mov", "mp4", "mpg"]
    MAX_CONTENT_LENGTH` = 1000 * 1024 * 1024  # 1000mb
    SQLALCHEMY_DATABASE_URI = "postgresql://localhost:5432/blog_db"
````


##### Setup
We can either pass the instance to FileUpload(app) or to the init_app(app) method:
````python
app = Flask(__name__)

db = SQLAlchemy()
# Important! See documentation for set up specifics
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
file_upload = FileUpload(app, db)

# An example using the Flask factory pattern
def create_app():
    db.init_app(app)
    file_upload.init_app(app)

# Or we can pass the Flask app instance directly & the Flask-SQLAlchemy instance:
db = SQLAlchemy(app)
file_upload = FileUpload(app, db)
app: Flask = None
````


##### Decorate your SqlAlchemy models
Flask-File-Upload (FFU) setup requires each SqlAlchemy model that wants to use FFU
library to be decorated with `@file_upload.Model` .This will enable FFU to update your
database with the extra columns required to store files in your database.
Declare your attributes as normal but assign a value of `file_upload.Column` &
pass the SqlAlchemy db instance: `file_upload.Column(db)`.
This is easy if you are using Flask-SqlAlchemy:
```python
from flask_sqlalchemy import SqlAlchemy

db = SqlAlchemy()
```
Full example:
 ````python
from my_app import db, file_upload

@file_upload.Model
class blogModel(db.Model):
    __tablename__ = "blogs"
    id = db.Column(db.Integer, primary_key=True)

    # Your files -  Notice how we pass in the SqlAlchemy instance
    # or `db` to the `file_uploads.Column` class:

    my_placeholder = file_upload.Column(db)
    my_video = file_upload.Column(db)
````

##### define files to be upload:
    (This is an example of a video with placeholder image attached):
````python
    my_video = request.files["my_video"]
    placeholder_img = request.files["placeholder_img"]
````


##### Save files
````python
    file_upload.save_files(blog_post, files={
        "my_video": my_video,
        "placeholder_img": placeholder_img,
    })
````

##### Update files
````python
    blog_post = file_upload.update_files(blog_post, files={
        "my_video": new_my_video,
        "placeholder_img": new_placeholder_img,
    })
````


##### Delete files

Deleting files from the db & server can be non trivial, especially to keep
both in sync. The `file_upload.delete_files` method can be called with a
kwarg of `clean_up` & then depending of the string value passed it will
provide 2 types of clean up functionality:
    - files will clean up files on the server but not update the model
    - model will update the model but not attempt to remove the files
      from the server.
See [delete_files Docs](https://flask-file-upload.readthedocs.io/en/latest/file_upload.html#flask_file_upload.file_upload.FileUpload.delete_files)
for more details
````python
    # Example using a SqlAlchemy model with an appended
    # method that fetches a single `blog`
    blogModel = BlogModel()
    blog_results = blogModel.get_one()
    
    # We pass the blog & files
    blog = file_upload.delete_files(blog_result, files=["my_video"])
    
    # As the `db` arg has not been passed to this method,
    # the changes would need persisting to the database:
    db.session.add(blog)
    db.session.commit()
    
    # If `db` is passed to this method then the updates are persisted.
    # to the session. And therefore the session has been commited.
    blog = file_upload.delete_files(blog_result, db, files=["my_video"])
````


##### Stream a file
````python
    file_upload.stream_file(blog_post, filename="my_video")
````


##### File Url paths
````python
    file_upload.get_file_url(blog_post, filename="placeholder_img")
````

