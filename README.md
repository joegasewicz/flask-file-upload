[![Upload Python Package](https://github.com/joegasewicz/flask-file-upload/actions/workflows/python-publish.yml/badge.svg)](https://github.com/joegasewicz/flask-file-upload/actions/workflows/python-publish.yml)
[![Python application](https://github.com/joegasewicz/flask-file-upload/actions/workflows/python-app.yml/badge.svg)](https://github.com/joegasewicz/flask-file-upload/actions/workflows/python-app.yml)
[![Documentation Status](https://readthedocs.org/projects/flask-file-upload/badge/?version=latest)](https://flask-file-upload.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/flask-file-upload.svg)](https://badge.fury.io/py/flask-file-upload)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/flask-file-upload)
![FlaskFileUpload](assets/logo.png?raw=true "Title")

Library that works with Flask (version 1 or 2) and SqlAlchemy to store
files on your server & in your database

Read the docs: [Documentation](https://flask-file-upload.readthedocs.io/en/latest/)

## Installation
Please install the latest release:
```bash
pip install flask-file-upload
```

*If you are updating from >=0.1 then please read the [upgrading instruction](https://github.com/joegasewicz/flask-file-upload#upgrading-from-v01-to-v02)*

#### General Flask config options
(Important: The below configuration variables need to be set  before initiating `FileUpload`)
````python
from flask_file_upload.file_upload import FileUpload
from os.path import join, dirname, realpath

# This is the directory that flask-file-upload saves files to. Make sure the UPLOAD_FOLDER is the same as Flasks's static_folder or a child. For example:
app.config["UPLOAD_FOLDER"] = join(dirname(realpath(__file__)), "static/uploads")

# Other FLASK config varaibles ...
app.config["ALLOWED_EXTENSIONS"] = ["jpg", "png", "mov", "mp4", "mpg"]
app.config["MAX_CONTENT_LENGTH"] = 1000 * 1024 * 1024  # 1000mb
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost:5432/blog_db"
````

#### Setup
We can either pass the instance to FileUpload(app) or to the init_app(app) method:
````python
from flask_file_upload import FileUpload


app = Flask(__name__, static_folder="static") # IMPORTANT: This is your root directory for serving ALL static content!

db = SQLAlchemy()

file_upload = FileUpload()

# An example using the Flask factory pattern
def create_app():
    db.init_app(app) 
    # Pass the Flask app instance as the 1st arg &
    # the SQLAlchemy object as the 2nd arg to file_upload.init_app.
    file_upload.init_app(app, db)
    
    # If you require importing your SQLAlchemy models then make sure you import
    # your models after calling `file_upload.init_app(app, db)` or `FileUpload(app, db)`. 
    from .model import * 

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

    # Use flask-file-upload's `file_upload.Column()` to associate a file with a SQLAlchemy Model:
    my_placeholder = file_upload.Column()
    my_video = file_upload.Column()
````

#### define files to be uploaded:
````python
# A common scenario could be a video with placeholder image.
# So first lets grab the files from Flask's request object:
my_video = request.files["my_video"]
placeholder_img = request.files["placeholder_img"]
````


#### Save files
To add files to your model, pass a dict of keys that reference the attribute
name(s) defined in your SqlAlchemy model & values that are your files.
For Example:

````python
file_upload.add_files(blog_post, files={
    "my_video": my_video,
    "placeholder_img": placeholder_img,
})

# Now commit the changes to your db
db.session.add(blog_post)
db.session.commit()
````
It's always good practise to commit the changes to your db as close to the end
of your view handlers as possible (we encourage you to use `add_files` over the `save_files`
method for this reason).

If you wish to let flask-file-upload handle adding & committing to
the current session then use `file_upload.save_files` - this method is only recommended
if you are sure nothing else needs committing after you have added you files.
For example:
```python
file_upload.save_files(blog_post, files={
    "my_video": my_video,
    "placeholder_img": placeholder_img,
})
```
##### If you followed the setup above you will see the following structure saved to your app:
![FlaskFileUpload](assets/dir1.png?raw=true "Directory example")

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

# If parent kwarg is set to True then the root primary directory & all its contents will be removed.
# The model will also get cleaned up by default unless set to `False`.
blog_result = file_upload.delete_files(blog_result, parent=True, files=["my_video"])


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

#### Set file paths to multiple objects - *Available in `0.1.0-rc.6` & `v0.1.0`*
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
assert  blogs[0].blog_image_url == "path/to/blogs/1/blog_image_url.png"
```

To set filename attributes to a a single or multiple SQLAlchemy parent models with backrefs
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

### Running Flask-Migration After including Flask-File-Upload in your project
The arguments below will also run if you're using vanilla Alembic.
```bash
export FLASK_APP=flask_app.py # Path to your Flask app

# with pip
flask db stamp head
flask db migrate
flask db upgrade

# with pipenv
pipenv run flask db stamp head
pipenv run flask db migrate
pipenv run flask db upgrade
```

### Upgrading from v0.1 to v0.2
You will need to create a migration script with the below column name changes:
- `[you_file_name]__file_type` becomes `[you_file_name]__mime_type`
- `[you_file_name]__mime_type` becomes `[you_file_name]__ext`
- `[you_file_name]__file_name` stays the same
