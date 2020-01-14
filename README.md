Update: A stable version -  `v0.1.0` of Flask-File-Upload will be released 
which will include `add_file_urls_to_models`. This will be released
on the 18/01/2020, thank you.

[![Build Status](https://travis-ci.org/joegasewicz/flask-file-upload.svg?branch=master)](https://travis-ci.org/joegasewicz/flask-file-upload)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/72eba439b16e43a295f956fe49e1b52f)](https://www.codacy.com/manual/joegasewicz/flask-file-upload?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=joegasewicz/flask-file-upload&amp;utm_campaign=Badge_Grade)
[![codecov](https://codecov.io/gh/joegasewicz/flask-file-upload/branch/master/graph/badge.svg)](https://codecov.io/gh/joegasewicz/flask-file-upload)
[![Documentation Status](https://readthedocs.org/projects/flask-file-upload/badge/?version=latest)](https://flask-file-upload.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/flask-file-upload.svg)](https://badge.fury.io/py/flask-file-upload)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/flask-file-upload)
![PyPI - License](https://img.shields.io/pypi/l/flask-file-upload?color=yellow)

![FlaskFileUpload](assets/logo.png?raw=true "Title")

Library that works with Flask & SqlAlchemy to store
files on your server & in your database

Read the docs: [Documentation](https://flask-file-upload.readthedocs.io/en/latest/)

## Installation
Please install the latest release candidate:
```bash
pip install flask-file-upload==0.1.0-rc.4
```

Flask File Upload


#### General Flask config options
````python
    # Important: The below configuration variables need to be set  before
    # initiating `FileUpload`
    app.config["UPLOAD_FOLDER"] = join(dirname(realpath(__file__)), "uploads/media")
    app.config["ALLOWED_EXTENSIONS"] = ["jpg", "png", "mov", "mp4", "mpg"]
    app.config["MAX_CONTENT_LENGTH"] = 1000 * 1024 * 1024  # 1000mb
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost:5432/blog_db"
````


#### Setup
We can either pass the instance to FileUpload(app) or to the init_app(app) method:
````python
app = Flask(__name__, static_folder="uploads/media") # Must be the save directory name as UPLOAD_FOLDER 

db = SQLAlchemy()

file_upload = FileUpload()

# An example using the Flask factory pattern
def create_app():
    db.init_app(app) 
    # Pass the Flask app instance as the 1st arg &
    # the SQLAlchemy object as the 2nd arg to file_upload.init_app.
    file_upload.init_app(app, db)

# Or we can pass the Flask app instance directly & the Flask-SQLAlchemy instance:
db = SQLAlchemy(app)
# Pass the Flask app instance as the 1st arg &
# the SQLAlchemy object as the 2nd arg to FileUpload
file_upload = FileUpload(app, db)
app: Flask = None
````


#### Decorate your SqlAlchemy models
Flask-File-Upload (FFU) setup requires each SqlAlchemy model that wants to use FFU
library to be decorated with `@file_upload.Model` .This will enable FFU to update your
database with the extra columns required to store files in your database.
Declare your attributes as normal but assign a value of `file_upload.Column`.
This is easy if you are using Flask-SqlAlchemy:
```python
from flask_sqlalchemy import SqlAlchemy

db = SqlAlchemy()
```
Full example:
 ````python
from my_app import file_upload

@file_upload.Model
class blogModel(db.Model):
    __tablename__ = "blogs"
    id = db.Column(db.Integer, primary_key=True)

    my_placeholder = file_upload.Column()
    my_video = file_upload.Column()
````

#### define files to be upload:
    (This is an example of a video with placeholder image attached):
````python
    my_video = request.files["my_video"]
    placeholder_img = request.files["placeholder_img"]
````


#### Save files
````python
    file_upload.save_files(blog_post, files={
        "my_video": my_video,
        "placeholder_img": placeholder_img,
    })
````

#### Update files
````python
    blog_post = file_upload.update_files(blog_post, files={
        "my_video": new_my_video,
        "placeholder_img": new_placeholder_img,
    })
````


#### Delete files

Deleting files from the db & server can be non trivial, especially to keep
both in sync. The `file_upload.delete_files` method can be called with a
kwarg of `clean_up` & then depending of the string value passed it will
provide 2 types of clean up functionality:
- `files` will clean up files on the server but not update the model
- `model` will update the model but not attempt to remove the files
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
    
    # If the kwarg `commit` is not set or set to True then the updates are persisted.
    # to the session. And therefore the session has been commited.
    blog = file_upload.delete_files(blog_result, files=["my_video"])
    
    # Example of cleaning up files but not updating the model:
    blog = file_upload.delete_files(blog_result, files=["my_video"], clean_up="files")
````


#### Stream a file
````python
    file_upload.stream_file(blog_post, filename="my_video")
````


#### File Url paths
````python
    file_upload.get_file_url(blog_post, filename="placeholder_img")
````

Example for getting file urls from many objects:
```python
    # If blogs_model are many blogs:
    for blog in blog_models:
        blog_image_url = file_upload.get_file_url(blog, filename="blog_image")
        setattr(blog, "blog_image", blog_image_url)
```

#### Set file paths to multiple objects - *Available in `v0.1.0`*
The majority of requests will require many entities to be returned
& these entities may have SQLAlchemy `backrefs` with
relationships that may also contain Flask-File-Upload (FFU) modified SQLAlchemy
models. To make this trivial, this method will set the appropriate
filename urls to your SQLAlchemy model objects (if the transaction
hasn't completed then **add_file_urls_to_models** will complete the
transaction by default).

The first argument required by this method is `models` - the SQLAlchemy model(s).

Then pass in the required kwarg `filenames` which references the parent's
FFU Model values - this is the `file_upload.Model` decorated SQLALchemy model
- `file_upload.Column()` method.

Important! Also take note that each attribute set by this method postfixes
a `_url` tag. e.g `blog_image` becomes `blog_image_url`

Example for many SQLAlchemy entity objects (*or rows in your table*)::
```python
    @file_upload.Model
    class BlogModel(db.Model):

        blog_image = file_upload.Column()
```

Now we can use the `file_upload.add_file_urls_to_models` to add file urls to
each SQLAlchemy object. For example::
```python
    blogs = add_file_urls_to_models(blogs, filenames="blog_image")

    # Notice that we can get the file path `blog_image` + `_url`
    assert  blogs[0].blog_image_url == "path/to/blogs/1/blog_image.png"
```

To set filename attributes to multiple SQLAlchemy parent models with backrefs
to multiple child SQLAlchemy models, we can assign to the optional `backref`
kwarg the name of the backref model & a list of the file attributes we set
with the FFU Model decorated SQLAlchemy model.

To use backrefs we need to declare a kwarg of `backref` & pass 2 keys:
    - **name**: The name of the backref relation
    - **filenames**: The FFU attribute values assigned to the backref model

For example::
```python
    # Parent model
    @file_upload.Model
    class BlogModel(db.Model):
        # The backref:
        blog_news = db.relationship("BlogNewsModel", backref="blogs")
        blog_image = file_upload.Column()
        blog_video = file_upload.Column()

    # Model that has a foreign key back up to `BlogModel
    @file_upload.Model
    class BlogNewsModel(db.Model):
        # The foreign key assigned to this model:
        blog_id = db.Column(db.Integer, db.ForeignKey("blogs.blog_id"))
        news_image = file_upload.Column()
        news_video = file_upload.Column()
```

The kwarg `backref` keys represent the backref model or entity (in the above example
this would be the `BlogNewsModel` which we have named `blog_news`. Example::
```python
    blogs = add_file_urls_to_models(blogs, filenames=["blog_image, blog_video"],
        backref={
            "name": "blog_news",`
            "filenames": ["news_image", "news_video],
    })
```

WARNING: You must not set the relationship kwarg: `lazy="dynamic"`!
If `backref` is set to *"dynamic"* then back-referenced entity's
filenames will not get set. Example::
```python
    # This will work
    blog_news = db.relationship("BlogNewsModel", backref="blog")

    # this will NOT set filenames on your model class
    blog_news = db.relationship("BlogNewsModel", backref="blog", lazy="dynamic")

```