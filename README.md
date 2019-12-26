![FlaskFileUpload](assets/logo.png?raw=true "Title")

### Work in progress...  

Library that works with Flask & SqlAlchemy to store
files in your database

## Installation

```bash
pip install flask-file-upload
```

Flask File Upload


##### General Flask config options
````python
    UPLOAD_FOLDER = join(dirname(realpath(__file__)), "uploads/lessons")
    ALLOWED_EXTENSIONS = ["jpg", "png", "mov", "mp4", "mpg"]
    MAX_CONTENT_LENGTH = 1000 * 1024 * 1024  # 1000mb
````


##### Setup
````python
    # my_app.py
    
    app = Flask(__name__)

    db = SQLAlchemy()
    file_upload = FileUpload()
    
    def create_app():
        db.init_app(app)
        file_upload.init_app(app)
        
    # Or we can pass directly:
    db = SQLAlchemy(app)
    file_upload = FileUpload(app)
````


##### FlaskFileUploads needs to do some work with your SqlAlchemy model
Decorate your SqlAlchemy model with file_upload's Model class:
 ````python
    from my_app import db, file_upload
    
    
    @file_upload.Model
    class ModelTest(db.Model):
        __tablename__ = "tests"
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


##### Get main form data and pass to your SqlAlchemy Model
````python
    blog_post = BlogPostModel(title="Hello World Today")
    
    file_upload.save_files(blog_post, files={
        "my_video": my_video,
        "placeholder_img": placeholder_img,
    })
````

##### Update file
````python
    blog_post = BlogPostModel(title="Hello World Today")
    blog_post = file_upload.update_files(blog_post, files={
        "my_video": new_my_video,
        "placeholder_img": new_placeholder_img,
    })
````


##### Delete files
````python
    file_upload.delete_files(BlogPostModel, files=["my_video"])
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

