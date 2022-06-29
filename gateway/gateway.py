from flask import Flask, request, jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException, default_exceptions

from . import handlers


app = Flask(__name__)


@app.errorhandler(Exception)
def handle_error(err):
    code = 500
    if isinstance(err, HTTPException):
        code = err.code
    elif isinstance(err, ValidationError):
        code = 400
    return jsonify(error=str(err)), code


for ex in default_exceptions:
    app.register_error_handler(ex, handle_error)


@app.route("/heartbeat")
def heartbeat() -> dict:
    return handlers.HeartbeatHandler().run(request.args)


@app.route("/sequence", methods=["POST"])
def add_to_sequence() -> dict:
    return handlers.AddToSequenceHandler().run(request.args, request.json)
