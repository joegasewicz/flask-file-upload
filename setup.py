from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="flask-file-upload",
    version="0.1.2",
    description="Library that works with Flask & SqlAlchemy to store files in your database and server.",
    packages=["flask_file_upload"],
    py_modules=["flask_file_upload"],
    install_requires=[
        'flask',
        'Flask-SQLAlchemy'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/joegasewicz/Flask-File-Upload",
    author="Joe Gasewicz",
    author_email="joegasewicz@gmail.com",
)
