
import json
import jsonschema
import logging
import inflection

from processor.reports.report_JSON import ReportJSON


logger = logging.getLogger(__name__)


def nanos_to_micros(nanos):
    return nanos // 10 ** 3

class Report:
    @staticmethod
    def load(report_file_path):
        with open(report_file_path) as fp:
            report = json.load(fp, cls=ReportJSONDecoder)
        report.file_path = report_file_path
        return report

    @staticmethod
    def get_gap_between_reports(second_report, first_report):
        return second_report.observations[0].day_timestamp - first_report.observations[0].day_timestamp

    def __init__(self,
                 from_dir, to_dir, packet_type,
                 initial_timestamp, reception_timestamp, sent_timestamp, final_timestamp,
                 public_key, observations, signature,
                 user_id, installation_id, file_path=None):
        self.from_dir = from_dir
        self.to_dir = to_dir
        self.packet_type = packet_type
        self.initial_timestamp = initial_timestamp
        self.reception_timestamp = reception_timestamp
        self.sent_timestamp = sent_timestamp
        self.final_timestamp = final_timestamp
        self.public_key = public_key
        self.observations = observations
        self.signature = signature
        self.user_id = user_id
        self.installation_id = installation_id
        self.file_path = file_path

    def get_observations_gap(self):
        return self.observations[-1].day_timestamp - self.observations[0].day_timestamp

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __hash__(self):
        return hash((self.from_dir,
                     self.to_dir,
                     self.packet_type,
                     self.initial_timestamp,
                     self.reception_timestamp,
                     self.sent_timestamp,
                     self.final_timestamp,
                     self.public_key,
                     self.observations,
                     self.signature,
                     self.user_id,
                     self.installation_id))

    def __repr__(self):
        return '{0!s}({1!r})'.format(self.__class__, self.__dict__)


class NotEnoughObservationsError(Exception):
    pass


class ReportJSONEncoder(json.JSONEncoder):
    @staticmethod
    def report_to_dict(report_object):
        report_dict = report_object.__dict__.copy()
        report_json = ReportJSON()
        json_fields_translations = report_json.get_JSON_fields_translations()
        for field_translation in json_fields_translations:
            field_value = report_dict.pop(field_translation.translation)
            report_dict[field_translation.original] = field_translation.reverse_translate(field_value)
        report_dict_fields = list(report_dict.keys())
        for field in report_dict_fields:
            inflexed_key = inflection.camelize(field, False)
            report_dict[inflexed_key] = report_dict.pop(field)
        fields_to_delete = []
        report_dict_fields = list(report_dict.keys())
        for field in report_dict_fields:
            if field not in report_json.get_JSON_report_schema()['required']:
                fields_to_delete.append(field)
        for field in fields_to_delete:
            report_dict.pop(field)
        return report_dict

    def default(self, obj):
        if isinstance(obj, Report):
            json_dict = self.report_to_dict(obj)
        else:
            json_dict = json.JSONEncoder.default(self, obj)
        return json_dict


class ReportJSONDecoder(json.JSONDecoder):
    @staticmethod
    def dict_to_report(json_dict):
        json_dict_keys = list(json_dict.keys())
        json_fields_translations = ReportJSON().get_JSON_fields_translations()
        for key in json_dict_keys:
            new_key = inflection.underscore(key)
            json_dict[new_key] = json_dict.pop(key)
        for field_translation in json_fields_translations:
            if field_translation.original in json_dict.keys():
                field_value = json_dict.pop(field_translation.original)
                json_dict[field_translation.translation] = field_translation.translate(field_value)
        return Report(**json_dict)

    def dict_to_object(self, d):
        try:
            json_schema = ReportJSON().get_JSON_report_schema()
            jsonschema.validate(d, json_schema)
            inst = self.dict_to_report(d)
        except jsonschema.ValidationError:
            inst = d
        return inst

    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.dict_to_object)