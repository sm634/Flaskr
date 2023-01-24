"""
This file contains the Application Factory and tells Python that the flask-tutorial directory should be treated as a package.
"""
import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app creates the Flask Instance. __name__ enables the app to know where the file is
    # located, so it can set up some paths. Instance_relative_config=True tells the app that the configuration files
    # are relative to the 'instance folder': https://flask.palletsprojects.com/en/2.2.x/config/#instance-folders.
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )

    if test_config is None:
        # load the instance config, if exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test_config if passed in.
        app.config.from_mapping(test_config)

    # ensure the instance folder exists.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')  # creates a connection between URL 'hello' and a function that returns a response (hello())
    def hello():
        return "Hello, World!"

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    return app

