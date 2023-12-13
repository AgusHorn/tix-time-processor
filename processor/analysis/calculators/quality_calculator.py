from processor.analysis.calculators.hurst_calculator import HurstCalculator
from processor.analysis.calculators.usage_calculator import UsageCalculator
from processor.analysis.utils import divide_observations_into_minutes


class QualityCalculator:
    DEFAULT_CONGESTION_THRESHOLD = 0.5
    DEFAULT_HURST_CONGESTION_THRESHOLD = 0.7

    def __init__(self, observations, hurst_calcultor, clock_fixer,
                 congestion_threshold=DEFAULT_CONGESTION_THRESHOLD,
                 hurst_congestion_threshold=DEFAULT_HURST_CONGESTION_THRESHOLD):
        self.observations = observations
        self.hurst_calculator = hurst_calcultor
        self.clock_fixer = clock_fixer
        self.congestion_threshold = congestion_threshold
        self.hurst_congestion_threshold = hurst_congestion_threshold
        self.observations_per_minute = divide_observations_into_minutes(self.observations)
        self.upstream_congestion, self.downstream_congestion = self._calculate_congestion()
        self.upstream_quality = \
            (len(self.observations_per_minute) - self.upstream_congestion) / len(self.observations_per_minute)
        self.downstream_quality = \
            (len(self.observations_per_minute) - self.downstream_congestion) / len(self.observations_per_minute)

    def _calculate_congestion(self):
        upstream_congestion = 0
        downstream_congestion = 0
        effective_upstream_hurst = HurstCalculator.calculate_effective_hurst(self.hurst_calculator.upstream_values)
        effective_downstream_hurst = HurstCalculator.calculate_effective_hurst(self.hurst_calculator.downstream_values)
        obspm_items = list(self.observations_per_minute.items())
        for minute, m_observations in obspm_items:
            if len(m_observations) < 30:
                self.observations_per_minute.pop(minute, None)
        for minute, m_observations in self.observations_per_minute.items():
            minute_usage_calculator = UsageCalculator(m_observations, self.clock_fixer)
            if minute_usage_calculator.upstream_usage < self.congestion_threshold \
                    and effective_upstream_hurst > self.hurst_congestion_threshold:
                upstream_congestion += 1
            if minute_usage_calculator.downstream_usage < self.congestion_threshold \
                    and effective_downstream_hurst > self.hurst_congestion_threshold:
                downstream_congestion += 1
        return upstream_congestion, downstream_congestion