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
        downstream_usage = downstream_over_threshold / downstream_over_mode
        return upstream_usage, downstream_usage