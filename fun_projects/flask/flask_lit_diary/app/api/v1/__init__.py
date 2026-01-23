from flask import Blueprint

api_v1 = Blueprint(
    "api_v1",
    __name__,
    url_prefix="/api/v1"
)

from . import notes, comments, users, auth  # it's important for the routes to be registered.
