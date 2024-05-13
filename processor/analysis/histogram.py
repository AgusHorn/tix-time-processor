from math import sqrt
from math import floor
import statistics

from processor.analysis.bin import Bin
from processor.analysis2 import observation_rtt_key_function


class FixedSizeBinHistogram:
    DEFAULT_ALPHA = 0.5

    def __init__(self, data, characterization_function, alpha=DEFAULT_ALPHA, debug=False):
        self.characterization_function = characterization_function
        self.alpha = alpha
        self.data = sorted(data, key=self.characterization_function)
        self.bins = list()
        self._generate_histogram()
        self.debug = debug
        self.bins_probabilities, self.mode, self.mode_index = self._generate_probabilities_mode_and_threshold()
    

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
        #probabilities = [(total_datapoints * total_width) / (len(bin_.data) * bin_.width) for bin_ in self.bins]
        #probabilities = [(len(bin_.data) / bin_.width) for bin_ in self.bins]
        probabilities = []
        for bin_ in self.bins:
            probabilities.append((len(bin_.data) / (bin_.width)))
        return list(probabilities)
    
    def find_mode_sorted_array(self, arr):
        data_cleared = list(map(lambda obs: self.characterization_function(obs), arr))
        print("&& DATA CLEARED &&")
        print(data_cleared)
        size = len(data_cleared)
        mode = None
        left = 0
        right = size - 1
        middle = int((size/2) - 1)
        while mode == None:
            if abs(left - right) == 1:
                mode = data_cleared[middle]
                break
            if (data_cleared[middle + 1] - data_cleared[left] <= data_cleared[right] - data_cleared[middle - 1]):
                right = middle
            else:
                left = middle
            middle = int(floor((right + left)/2))
        return mode, middle

        
    
    # def find_mode(self, arr):
    #     data_cleared = list(map(lambda obs: self.characterization_function(obs), self.data))
    #     max_count = 0
    #     mode = None
    #     index = 0
    #     final_index = 0
    #     current_count = 0
    #     current_number = None

    #     for num in arr:
    #         if num != current_number:
    #             current_number = num
    #             current_count = 1
    #         else:
    #             current_count += 1

    #         if current_count > max_count:
    #             max_count = current_count
    #             mode = current_number
    #             final_index = index 
    #         index += 1
            

    #     return mode,index


    def _generate_probabilities_mode_and_threshold(self):
        
        probabilities = self._generate_bins_probabilities()
        representative_bins = 2 * int(sqrt(len(self.bins)))
        representative_probabilities = probabilities[:representative_bins]
        # print("## REP PROBS ##")
        # print(representative_probabilities)
        # print(max(representative_probabilities))
        # mode_index = representative_probabilities.index(max(representative_probabilities))
        # mode_val = self.bins[mode_index].mid_value
        # print(mode_index)
        # print(mode_val)
        #print("##### DATA #####")
        #print([observation_rtt_key_function(data) for data in self.data])
        
        mode, mode_index = self.find_mode_sorted_array(self.data)
        
        
        # index = self.data.index(mode)
        # bins_qty = int(floor(sqrt(len(self.data))))
        # datapoints_per_bin = len(self.data) // bins_qty
        # bin_index = floor(index / datapoints_per_bin)
        # mode_value = self.bins[bin_index].mid_value
        
        # mode = max(representative_probabilities)
        # mode_index = representative_probabilities.index(mode)
        # mode_value = self.bins[mode_index].mid_value
        
        if self.debug:
            print('### MODE ###')
            print(mode)

        # if representative_probabilities[0] == mode:
        #     threshold = self.bins[1].mid_value
        # else:
        # data_cleared = list(map(lambda obs: self.characterization_function(obs), self.data))
        # threshold = (mode - data_cleared[0]) * (self.alpha) + mode
        # # if self.debug:
        # #     print('### Data_cleared[0] ###')
        # #     print(data_cleared[0])
        # #     print('### MODE WITH PYTHON####')
        # #     print(statistics.mode(data_cleared))
        # threshold = 9454785.64453125
        
        #threshold = mode + (data_cleared[floor(len(data_cleared)/2)] - data_cleared[0]) * (self.alpha)
        return probabilities, mode, mode_index
