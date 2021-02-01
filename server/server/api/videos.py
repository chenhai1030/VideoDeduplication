import os
from http import HTTPStatus
from os.path import dirname, basename

from flask import abort, send_from_directory

from db.schema import Files
from .blueprint import api
from .helpers import resolve_video_file_path, download_file
from ..model import database


@api.route('/files/<int:file_id>/watch')
def watch_video(file_id):
    file = database.session.query(Files).filter(Files.id == file_id).first()

    # Handle file not found
    if file is None:
        abort(HTTPStatus.NOT_FOUND.value, f"File id not found: {file_id}")

    if file.file_url is not None:
        return download_file(file.file_url)

    path = resolve_video_file_path(file.file_path)
    if not os.path.isfile(path):
        abort(HTTPStatus.NOT_FOUND.value, f"Video file is missing: {file.file_path}")
    else:
        return send_from_directory(dirname(path), basename(path))
