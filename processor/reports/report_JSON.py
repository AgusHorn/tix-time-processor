import base64
import struct
from processor.reports.field_translation import FieldTranslation
from processor.reports.observation import Observation
from processor.reports.report_field_types import ReportFieldTypes
from processor.reports.serialized_observation import SerializedObservation

class ReportJSON:

    def get_JSON_report_schema(self):
        return {
            "type": "object",
            "properties": {
                "from": {
                    "anyOf": [
                        {"type": "string", "format": "ipv4"},
                        {"type": "string", "format": "ipv6"},
                        {"type": "string", "format": "hostname"}
                    ]
                },
                "to": {
                    "anyOf": [
                        {"type": "string", "format": "ipv4"},
                        {"type": "string", "format": "ipv6"},
                        {"type": "string", "format": "hostname"}
                    ]
                },
                "type": {
                    "type": "string",
                    "enum": ["LONG"]
                },
                "initialTimestamp": {"type": "integer"},
                "receptionTimestamp": {"type": "integer"},
                "sentTimestamp": {"type": "integer"},
                "finalTimestamp": {"type": "integer"},
                "publicKey": {"type": "string"},
                "message": {"type": "string"},
                "signature": {"type": "string"},
                "userId": {"type": "integer"},
                "installationId": {"type": "integer"}
            },
            "required": [
                "from", "to", "type",
                "initialTimestamp", "receptionTimestamp", "sentTimestamp", "finalTimestamp",
                "publicKey", "message", "signature",
                "userId", "installationId"
            ]
        } 

    def get_JSON_fields_translations(self):
        return [
            FieldTranslation("from", "from_dir"),
            FieldTranslation("to", "to_dir"),
            FieldTranslation("type", "packet_type"),
            FieldTranslation("message", "observations", self.__deserialize_observations, self.__serialize_observations)
        ]

    def __deserialize_observations(self, message):
        bytes_message = base64.b64decode(message)
        observations = []
        for message_index in range(0, len(bytes_message), SerializedObservation.byte_size):
            line = bytes_message[message_index:message_index + SerializedObservation.byte_size]
            observation_dict = {}
            line_struct_format = ReportFieldTypes.endian_type
            for field in SerializedObservation.fields:
                line_struct_format += field.type.struct_type
            line_tuple = struct.unpack(line_struct_format, line)
            for field_index in range(len(SerializedObservation.fields)):
                field = SerializedObservation.fields[field_index]
                observation_dict[field.name] = line_tuple[field_index]
            observations.append(Observation(**observation_dict))
        return observations
    
    def __serialize_observations(self, observations):
        bytes_message = bytes()
        for observation in observations:
            observation_bytes = bytes()
            for field in SerializedObservation.fields:
                field_bytes = struct.pack(field.type.get_struct_representation(), getattr(observation, field.name))
                observation_bytes = b''.join([observation_bytes, field_bytes])
            bytes_message = b''.join([bytes_message, observation_bytes])
        return base64.b64encode(bytes_message).decode()
