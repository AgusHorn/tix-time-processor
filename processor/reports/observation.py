class Observation:
    def __init__(self, day_timestamp, type_identifier, packet_size,
                 initial_timestamp, reception_timestamp, sent_timestamp, final_timestamp):
        self.day_timestamp = day_timestamp
        self.type_identifier = type_identifier
        self.packet_size = packet_size
        self.initial_timestamp_nanos = initial_timestamp
        self.reception_timestamp_nanos = reception_timestamp
        self.sent_timestamp_nanos = sent_timestamp
        self.final_timestamp_nanos = final_timestamp
        self.upstream_phi = 0.0
        self.downstream_phi = 0.0
        self.estimated_phi = 0.0

    @property
    def initial_timestamp(self):
        return self.initial_timestamp_nanos

    @property
    def reception_timestamp(self):
        return self.reception_timestamp_nanos

    @property
    def sent_timestamp(self):
        return self.sent_timestamp_nanos

    @property
    def final_timestamp(self):
        return self.final_timestamp_nanos

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __hash__(self):
        return hash((self.day_timestamp,
                     self.type_identifier,
                     self.packet_size,
                     self.initial_timestamp_nanos,
                     self.reception_timestamp_nanos,
                     self.sent_timestamp_nanos,
                     self.final_timestamp_nanos))

    def __repr__(self):
        return '{0!s}({1!r})'.format(self.__class__, self.__dict__)