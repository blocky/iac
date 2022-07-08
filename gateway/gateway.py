import toml

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException, default_exceptions

from . import handlers
from . import serializers


app = Flask(__name__)

# configure auth
app.config.from_file("config/config.toml", toml.load)
app.config.from_prefixed_env("BKY_SEQ_GATEWAY")
app.config["JWT_ERROR_MESSAGE_KEY"] = "error"
JWTManager(app)


@app.errorhandler(Exception)
def handle_error(err):
    if isinstance(err, HTTPException):
        code = err.code
        error_data = str(err)
    elif isinstance(err, ValidationError):
        code = 400
        error_data = err.messages
    elif isinstance(err, serializers.ConfigurationLoadError):
        code = 500
        error_data = err.messages
    else:
        code = 500
        error_data = str(err)
    return jsonify(error=error_data), code


for ex in default_exceptions:
    app.register_error_handler(ex, handle_error)


@app.route("/heartbeat")
def heartbeat() -> dict:
    return handlers.HeartbeatHandler(app.config).run(request.args)


@app.route("/sequence", methods=["POST"])
@jwt_required()
def add_to_sequence() -> dict:
    return handlers.AddToSequenceHandler().run(request.args, request.json)
