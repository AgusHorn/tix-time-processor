
import base64
import json
import struct
import logging
from processor.reports.observation import Observation
from processor.reports.report_field_types import ReportFieldTypes
from processor.reports.serialized_observation import SerializedObservation

logger = logging.getLogger(__name__)

class Batch:

    def __init__(self, from_dir = '', to_dir = '', initial_timestamp = 0, final_timestamp = 0, observations = []):
        self.from_dir = from_dir
        self.to_dir = to_dir
        self.initial_timestamp = initial_timestamp
        self.final_timestamp = final_timestamp
        self.observations = observations

    def __repr__(self):
        return '{0!s}({1!r})'.format(self.__class__, self.__dict__)
    
    def __serialize_observations(self):
        bytes_message = bytes()
        for observation in self.observations:
            observation_bytes = bytes()
            for field in SerializedObservation.fields:
                field_bytes = struct.pack(field.type.get_struct_representation(), getattr(observation, field.name))
                observation_bytes = b''.join([observation_bytes, field_bytes])
            bytes_message = b''.join([bytes_message, observation_bytes])
        return base64.b64encode(bytes_message).decode()
    
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
    
    def save(self, filepath):
        try: 
            with open(filepath, 'x') as fp:
                self.observations = self.__serialize_observations()
                json_batch = json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
                fp.write(json_batch)
            return json_batch
        except FileExistsError: 
            print(f"The file '{filepath}' already exists.")
    
    def load(self, filepath):
        try: 
            with open(filepath, 'r') as fp:
                line = fp.read()
                batch = json.loads(line, object_hook=lambda d: Batch(**d))
                batch.observations = self.__deserialize_observations(batch.observations)
                return batch
        except FileNotFoundError: 
            print(f"The file '{filepath}' does not exists.")


class NotEnoughObservationsError(Exception):
    pass