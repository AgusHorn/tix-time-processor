from functools import partial

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
        self.downstream_histogram = FixedSizeBinHistogram(observations, self.downstream_time_key_function)
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
        # correct_threshold = self.find_threshold_for_area(sorted_times, 0.0000005242074565)
        # print("##### CORRECT THRESHOLD FOUND")
        # print(correct_threshold)
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
    
    # def find_threshold_for_area(self, observations, target_area, tolerance=0.000000001):
    #     # Establecer límites para la búsqueda binaria
    #     lower_bound = min(observations)
    #     upper_bound = max(observations)
        
    #     # Realizar búsqueda binaria
    #     while lower_bound <= upper_bound:
    #         mid = (lower_bound + upper_bound) / 2
            
    #         # Calcular el área usando el algoritmo existente con el umbral actual
    #         area = self._generate_area_under_curve(observations, mid)
            
    #         # Comparar el área calculada con el objetivo
    #         if abs(area - target_area) < tolerance:
    #             # Si la diferencia está dentro de la tolerancia, devolver el umbral
    #             return mid
    #         elif area < target_area:
    #             # Si el área es menor que el objetivo, ajustar el límite inferior
    #             lower_bound = mid + tolerance
    #         else:
    #             # Si el área es mayor que el objetivo, ajustar el límite superior
    #             upper_bound = mid - tolerance
        
    #     print(lower_bound)
    #     print(upper_bound)
    #     # Si no se encontró un umbral dentro de la tolerancia, devolver None
    #     return None