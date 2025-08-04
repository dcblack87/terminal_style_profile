from flask import Blueprint

bp = Blueprint('blog', __name__)

from app.blueprints.blog import routes