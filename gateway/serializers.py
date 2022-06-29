from marshmallow import Schema, fields


class HeartbeatSerializer(Schema):
    status = fields.Function(lambda x: x.status.value, required=True)


class AddToSequenceSerializer(Schema):
    data = fields.Str(required=True)


class AttestationSerializer(Schema):
    attestation = fields.Str(required=True)
    data = fields.Str(required=True)
    idx = fields.Int(required=True)
    created_at = fields.DateTime(required=True, format="iso")
