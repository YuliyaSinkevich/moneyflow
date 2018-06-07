from flask import Blueprint, render_template

from app import app

home = Blueprint('home', __name__)

from app.home import routes


@home.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


app.register_error_handler(404, page_not_found)
