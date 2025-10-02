from flask import Blueprint, send_from_directory
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

dashboard = Blueprint("dashboard", __name__)

@dashboard.route("/")
def index():
    # Serve index.html from static folder
    return send_from_directory(STATIC_DIR, "index.html")
