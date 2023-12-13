from processor.reports.report_field_types import ReportFieldTypes


class SerializedObservationField:
    def __init__(self, name, report_field_type):
        self.name = name
        self.type = report_field_type


class SerializedObservation:
    fields = [
        # Timestamp in seconds since UNIX epoch of the time the packet was sent to the server
        SerializedObservationField('day_timestamp', ReportFieldTypes.Long),
        # Byte indicating if is a Long or Short packet
        SerializedObservationField('type_identifier', ReportFieldTypes.Char),
        # Size of the packet when it was sent to the server
        SerializedObservationField('packet_size', ReportFieldTypes.Integer),
        # The timestamp in nanoseconds since the start of the day in local time
        # from when the packet was sent by the client to the server
        SerializedObservationField('initial_timestamp', ReportFieldTypes.Long),
        # The timestamp in nanoseconds since the start of the day in local time
        # from when the packet was received by the server
        SerializedObservationField('reception_timestamp', ReportFieldTypes.Long),
        # The timestamp in nanoseconds since the start of the day in local time
        # from when the packet was sent by the server to the client
        SerializedObservationField('sent_timestamp', ReportFieldTypes.Long),
        # The timestamp in nanoseconds since the start of the day in local time
        # from when the packet was received by the client
        SerializedObservationField('final_timestamp', ReportFieldTypes.Long),
    ]
    byte_size = sum([field.type.byte_size for field in fields])