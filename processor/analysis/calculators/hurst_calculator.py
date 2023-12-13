from math import floor, log as log_function
from processor import hurst
from processor.analysis.utils import downstream_time_function, upstream_time_function

class HurstCalculator:
    @staticmethod
    def calculate_effective_hurst(hurst_values):
        return (hurst_values['wavelet'] + hurst_values['rs']) / 2

    @staticmethod
    def hurst_values(data):
        wavelet_hurst = hurst.wavelet(data)
        rs_hurst = hurst.rs(data)
        return {
            'wavelet': wavelet_hurst,
            'rs': rs_hurst
        }

    def __init__(self, observations, clock_fixer):
        self.observations = observations
        self.capped_observations = self._cap_observations()
        self.clock_fixer = clock_fixer
        self.upstream_times, self.downstream_times = self._calculate_times()
        self.upstream_values = self.hurst_values(self.upstream_times)
        self.downstream_values = self.hurst_values(self.downstream_times)

    def _calculate_desired_length(self):
        return int(2 ** floor(log_function(len(self.observations), 2)))

    def _cap_observations(self):
        desired_length = self._calculate_desired_length()
        capped_observations = self.observations[-desired_length:]
        return capped_observations

    def _calculate_times(self):
        upstream_times = []
        downstream_times = []
        for observation in self.capped_observations:
            upstream_time = upstream_time_function(observation, self.clock_fixer.phi_function)
            downstream_time = downstream_time_function(observation, self.clock_fixer.phi_function)
            upstream_times.append(upstream_time)
            downstream_times.append(downstream_time)
        return upstream_times, downstream_times
