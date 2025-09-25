import os
from flask import Flask

backend_host = os.environ.get("BACKEND_HOST")
backend_port = os.environ.get("BACKEND_PORT")


def create_app():
    app = Flask(__name__)
    return app
