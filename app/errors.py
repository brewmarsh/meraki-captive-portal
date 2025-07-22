from flask import Blueprint, render_template
from . import db
import logging

bp = Blueprint('errors', __name__)

@bp.app_errorhandler(404)
def not_found_error(error):
    logging.error(f"404 error: {error}")
    return render_template('404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logging.error(f"500 error: {error}", exc_info=True)
    return render_template('500.html'), 500
