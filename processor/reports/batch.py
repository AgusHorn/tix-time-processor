
import base64
import json
import struct
import logging
from processor.reports.report_JSON import ReportJSON
from processor.reports.serialized_observation import SerializedObservation

logger = logging.getLogger(__name__)

class Batch:

    def __init__(self, from_dir, to_dir, initial_timestamp, final_timestamp, observations):
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
    
    def save(self, filepath):
        try: 
            with open(filepath, 'x') as fp:
                self.observations = self.__serialize_observations()
                json_batch = json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
                fp.write(json_batch)
            return json_batch
        except FileExistsError: 
            print(f"The file '{filepath}' already exists.") 


class NotEnoughObservationsError(Exception):
    pass