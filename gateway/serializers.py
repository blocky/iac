from marshmallow import (
    Schema,
    fields,
    post_load,
    validate,
    EXCLUDE,
    ValidationError,
)

from gateway.exception import GatewayError
from gateway.models import values_as_strs, JWTAlgorithm, Configuration


class ConfigurationLoadError(GatewayError):
    def __init__(self, msg: str, err: ValidationError):
        super().__init__(msg)
        self._validation_error = err

    @property
    def messages(self) -> dict:
        return self._validation_error.messages


class ConfigurationSerializer(Schema):
    JWT_ALGO_KEY = "JWT_ALGORITHM"
    JWT_PUBLIC_KEY_KEY = "JWT_PUBLIC_KEY"

    class Meta:
        unknown = EXCLUDE

    jwt_algorithm = fields.Str(
        required=True,
        validate=validate.OneOf(values_as_strs(JWTAlgorithm)),
        data_key=JWT_ALGO_KEY,
    )
    jwt_public_key = fields.Str(
        required=True,
        data_key=JWT_PUBLIC_KEY_KEY,
    )

    @post_load
    def make(self, data, **_kwargs):
        return Configuration(**data)

    def load_with_custom_error(self, data) -> Configuration:
        try:
            return ConfigurationSerializer().load(data)
        except ValidationError as err:
            raise ConfigurationLoadError("Invalid configuration", err) from err


class HeartbeatSerializer(Schema):
    status = fields.Str(required=True)
    configuration = fields.Nested(ConfigurationSerializer, required=True)


class AddToSequenceSerializer(Schema):
    data = fields.Str(required=True)


class AttestationSerializer(Schema):
    attestation = fields.Str(required=True)
    data = fields.Str(required=True)
    idx = fields.Int(required=True)
    created_at = fields.DateTime(required=True, format="iso")
