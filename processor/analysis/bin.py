class Bin:
    def __init__(self, data, characterization_function):
        self.data = list(data)
        self.characterization_function = characterization_function

    def __str__(self):
        return str({
            "LenData": len(self.data),
            "MaxValue": self.max_value,
            "MinValue": self.min_value,
            "Width": self.width,
            "MidValue": self.mid_value
        })

    def update(self, new_data):
        self.data.extend(list(new_data))

    @property
    def max_value(self):
        return self.characterization_function(max(self.data, key=self.characterization_function))

    @property
    def min_value(self):
        return self.characterization_function(min(self.data, key=self.characterization_function))

    @property
    def width(self):
        return self.max_value - self.min_value

    @property
    def mid_value(self):
        return self.min_value + self.width // 2