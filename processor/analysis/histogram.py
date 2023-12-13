from math import sqrt
from math import floor

from processor.analysis.bin import Bin


class FixedSizeBinHistogram:
    DEFAULT_ALPHA = 0.5

    def __init__(self, data, characterization_function, alpha=DEFAULT_ALPHA):
        self.characterization_function = characterization_function
        self.alpha = alpha
        self.data = sorted(data, key=self.characterization_function)
        self.bins = list()
        self._generate_histogram()
        self.bins_probabilities, self.mode, self.threshold = self._generate_probabilities_mode_and_threshold()

    def _generate_histogram(self):
        bins_qty = int(floor(sqrt(len(self.data))))
        datapoints_per_bin = len(self.data) // bins_qty
        # Create a histogram with the same amount of observation in each bin
        threshold = 0
        for index in range(bins_qty):
            data_index = index * datapoints_per_bin
            threshold = data_index + datapoints_per_bin
            bin_data = self.data[data_index:threshold]
            bin_ = Bin(bin_data, self.characterization_function)
            self.bins.append(bin_)
        # If there still some observations left, we add them to the last bin
        if threshold < len(self.data):
            self.bins[-1].update(self.data[threshold:])

    def _generate_bins_probabilities(self):
        total_datapoints = sum([len(bin_.data) for bin_ in self.bins])
        total_width = self.bins[-1].max_value - self.bins[0].min_value
        probabilities = [(total_datapoints * total_width) / (len(bin_.data) * bin_.width)
                         for bin_ in self.bins]
        return list(probabilities)

    def _generate_probabilities_mode_and_threshold(self):
        probabilities = self._generate_bins_probabilities()
        representative_bins = 2 * int(sqrt(len(self.bins)))
        representative_probabilities = probabilities[:representative_bins]
        mode = max(representative_probabilities)
        mode_index = representative_probabilities.index(mode)
        mode_value = self.bins[mode_index].mid_value
        if representative_probabilities[0] == mode:
            threshold = self.bins[1].mid_value
        else:
            threshold = mode_value + self.alpha * self.bins[0].mid_value
        return probabilities, mode_value, threshold
