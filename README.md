# Flask File Upload

Library that works with Flask & SqlAlchemy to store
files in your database

## Installation

```bash
pip install flask-file-upload
```

Flask File Upload

# Public api:

    file_uploads = FileUploads(app)

##### General Flask config options
````python
    UPLOAD_FOLDER = join(dirname(realpath(__file__)), "uploads/lessons")
    ALLOWED_EXTENSIONS = ["jpg", "png", "mov", "mp4", "mpg"]
    MAX_CONTENT_LENGTH = 1000 * 1024 * 1024  # 1000mb
````


##### Setup
````python
    db = SQLAlchemy()
    file_uploads = FileUploads()
````


##### FlaskFileUploads needs to do some work with your SqlAlchemy model
Decorate your SqlAlchemy model with file_uploads's Model class:
 ````python
    @file_uploads.Model
    class ModelTest(db.Model):
        __tablename__ = "tests"
        id = db.Column(db.Integer, primary_key=True)
        # Your files -  Notice how we pass in the SqlAlchemy instance
        # (in this case we named it `db`) to the `file_uploads.Column` class:
        my_placeholder = file_uploads.Column(db)
        my_video = file_uploads.Column(db)
````

##### define files to be upload:
    (This is an example of a video with placeholder image attached):
````python
    my_video = request.files["my_video"]
    placeholder_img = request.files["placeholder_img"]
````


##### Get main form data and pass to your SqlAlchemy Model
````python
    blog_post = BlogPostModel(title="Hello World Today")
    
    file_uploads.save_files(blog_post, files={
        "my_video": my_video,
        "placeholder_img": placeholder_img,
    })
````

##### Update files
````python
    file_uploads.update_files(BlogPostModel, files=[my_video])
````


##### Update file name
````python
    file_uploads.update_file_name(BlogPostModel, my_video, new_filename="new_name")
````


##### Stream a file
````python
    First get your entity
    my_blog_post = BlogModel().get(id=1)  # Or your way of getting an entity
    file_upload.stream_file(blog_post, filename="my_video")
````


##### File Url paths
````python
    file_upload.get_file_url(blog_post, filename="placeholder_img")
````

