from functools import partial
import numpy as np
from processor.analysis.histogram import FixedSizeBinHistogram
from processor.analysis.utils import downstream_time_function, upstream_time_function

class UsageCalculator:
    def __init__(self, observations, clock_fixer):
        self.observations = observations
        self.clock_fixer = clock_fixer
        self.upstream_time_key_function = partial(upstream_time_function,
                                                  phi_function=self.clock_fixer.phi_function)
        self.downstream_time_key_function = partial(downstream_time_function,
                                                    phi_function=self.clock_fixer.phi_function)
        self.upstream_histogram = FixedSizeBinHistogram(observations, self.upstream_time_key_function)
        self.downstream_histogram = FixedSizeBinHistogram(observations, self.downstream_time_key_function, 0.5,True)
        self.upstream_usage, self.downstream_usage = self._calculate_usage()

    def _calculate_usage(self):
        #print("#### DOWNSTREAM MODE ######")
        #print(self.downstream_histogram.mode)
        upstream_over_threshold = 0
        downstream_over_threshold = 0
        upstream_over_mode = 0
        downstream_over_mode = 0
        for observation in self.observations:
            upstream_time = self.upstream_time_key_function(observation)
            downstream_time = self.downstream_time_key_function(observation)
            if upstream_time > self.upstream_histogram.threshold:
                upstream_over_threshold += 1
            if downstream_time > self.downstream_histogram.threshold:
                downstream_over_threshold += 1
            if upstream_time > self.upstream_histogram.mode:
                upstream_over_mode += 1
            if downstream_time > self.downstream_histogram.mode:
                downstream_over_mode += 1
        upstream_usage = upstream_over_threshold / upstream_over_mode

        # downstream_usage = downstream_over_threshold / downstream_over_mode
        print("@@@ DOWNSTREAM THRESHOLD @@@")
        print(self.downstream_histogram.threshold)
        print("@@@ DOWNSTREAM MODE @@@")
        print(self.downstream_histogram.mode)
        
        downstream_times = list(map(lambda obs: self.downstream_time_key_function(obs), self.observations))
        sorted_times = sorted(downstream_times)
        correct_threshold = self.find_threshold_for_area(sorted_times, self.downstream_histogram.mode)
        print("##### CORRECT THRESHOLD FOUND")
        print(correct_threshold)
        # for downstream_time in downstream_times_sorted:
        #     correct_area_from_threshold = self._generate_area_under_curve(self.observations,downstream_time)
        #     print(str(correct_area_from_threshold) + "-" + str(downstream_time) )
        #     if (correct_area_from_threshold == 0.0000005242074565):
        #         print("##### CORRECT THRESHOLD FOUND")
        #         print(correct_area_from_threshold)

        area_from_threshold = self._generate_area_under_curve(sorted_times,self.downstream_histogram.threshold)
        print("#### Area from Threshold ######")
        print(area_from_threshold)       
        area_from_mode = self._generate_area_under_curve(sorted_times, self.downstream_histogram.mode)
        print("#### Area MODE ######")
        print(area_from_mode)
        print("#### Longitud de mediciones ######")
        print(len(sorted_times))
        print("#### Minimo ######")
        print(sorted_times[0])
        print("#### Maximo ######")
        print(sorted_times[-1])
        print("#### Quartil 25% ######")
        print(np.percentile(sorted_times, 25))
        print("#### Quartil 50% ######")
        print(np.percentile(sorted_times, 50))
        print("#### Quartil 75% ######")
        print(np.percentile(sorted_times, 75))
        

        if (area_from_mode != 0): 
            downstream_usage = float(area_from_threshold) / float(area_from_mode) 
        else:
            downstream_usage = 0
        return upstream_usage, downstream_usage
    
    def _generate_area_under_curve(self, observations, threshold=0):
        accumulator = 0
        previous_value = 0
        count_same_value = 1
        #downstream_times = list(map(lambda obs: self.downstream_time_key_function(obs), observations))
        #downstream_times_sorted = sorted(observations)
        for i in range(1, len(observations), 1):
            if (threshold != 0 and observations[i] < threshold):
                continue
            value = float(observations[i]) - float(observations[i-1])
            if (value == previous_value):
                count_same_value += 1
                continue
            if (count_same_value != 1):
                accumulator += (count_same_value / previous_value)
            accumulator += 1/value
            previous_value = value
            count_same_value = 1
        return accumulator
    
    def find_threshold_for_area(self, observations, mode):
        final_area = 0.0003274646992
        area = 0.0000
        begin = mode
        end = observations[-1]
        threshold = float((begin + end) / 2)
        while True:
            print("#AREA# {}".format(area))
            print("#THRESHOLD# {}".format(threshold))
            print("#BEGIN# {}".format(begin))
            print("#END# {}".format(end))
            area = self._generate_area_under_curve(observations, threshold)
            area_decimal = round(area, 5)
            final_area_decimal = round(final_area, 5)
            print("#AREA_decimal# {}".format(area_decimal))
            print("#AREAFINAL_decimal# {}".format(final_area_decimal))
            if area_decimal == final_area_decimal or round(area,2) + 0.01 == round(final_area,2) or round(end,8) == round(begin,8):
                return threshold, area, begin, end
            if area < final_area:
                end = threshold
                threshold = float((begin + end) / 2)
            elif area > final_area:
                begin = threshold
                threshold = float((begin + end) / 2)
            



        