class ReportFieldTypes:
    class ReportFieldType:
        def __init__(self, name, byte_size, struct_type):
            self.name = name
            self.byte_size = byte_size
            self.struct_type = struct_type

        def get_struct_representation(self):
            return ReportFieldTypes.endian_type + self.struct_type

    endian_type = '>'
    Integer = ReportFieldType('int', 4, 'i')
    Char = ReportFieldType('char', 1, 'c')
    Long = ReportFieldType('long', 8, 'q')
