from datetime import timedelta
import logging
from operator import attrgetter
from processor.analysis.calculators.hurst_calculator import HurstCalculator
from processor.analysis.calculators.quality_calculator import QualityCalculator
from processor.analysis.calculators.usage_calculator import UsageCalculator
from processor.analysis.clock_fixer import ClockFixer

from processor.analysis.histogram import FixedSizeBinHistogram
from processor.analysis.utils import observation_rtt_key_function

class Analyzer:
    MEANINGFUL_OBSERVATIONS_DELTA = timedelta(minutes=10)

    CONGESTION_THRESHOLD = 0.5
    HURST_CONGESTION_THRESHOLD = 0.7

    def __init__(self, observations_set):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.observations = [observation for observation in observations_set if observation.type_identifier == b'S']
        #self.meaningful_observations = self.calculate_meaningful_observations()
        self.meaningful_observations = self.observations
        self.rtt_histogram = FixedSizeBinHistogram(data=self.observations,characterization_function=observation_rtt_key_function)
        self.clock_fixer = ClockFixer(self.rtt_histogram.bins[0].data, tau=self.rtt_histogram.mode)
        self.usage_calculator = UsageCalculator(self.meaningful_observations, self.clock_fixer)
        self.hurst_calculator = HurstCalculator(self.meaningful_observations, self.clock_fixer)
        # self.quality_calculator = QualityCalculator(self.meaningful_observations,
        #                                              self.hurst_calculator,
        #                                              self.clock_fixer)

    def calculate_meaningful_observations(self):
        sorted_observations = sorted(self.observations, key=attrgetter('day_timestamp'))
        first_observation = sorted_observations[0]
        last_observation = sorted_observations[-1]
        observations_delta = timedelta(seconds=(last_observation.day_timestamp - first_observation.day_timestamp))
        if observations_delta < self.MEANINGFUL_OBSERVATIONS_DELTA:
            raise ValueError('Meaningful observations time delta is lower than expected. '
                             'Expected {}, got {}'.format(self.MEANINGFUL_OBSERVATIONS_DELTA, observations_delta))
        meaningful_threshold_timestamp = last_observation.day_timestamp \
                                         - self.MEANINGFUL_OBSERVATIONS_DELTA.total_seconds()
        meaningful_observations = [observation for observation in self.observations
                                   if observation.day_timestamp > meaningful_threshold_timestamp]
        return meaningful_observations

    def get_results(self):
        logger = self.logger.getChild('get_results')
        results = {
            'timestamp': self.meaningful_observations[-1].day_timestamp,
            'upstream': {
                'usage': self.usage_calculator.upstream_usage,
                'quality': 0,
                'hurst': self.hurst_calculator.upstream_values
            },
            'downstream': {
                'usage': self.usage_calculator.downstream_usage,
                'quality': 0,
                'hurst': self.hurst_calculator.downstream_values
            },
            'dataFromReport': {
                'LongMediciones': self.usage_calculator.long_mediciones if hasattr(self.usage_calculator, 'long_mediciones') else 0,
                'Minimo': self.usage_calculator.min if hasattr(self.usage_calculator, 'min') else 0,
                'Maximo': self.usage_calculator.max if hasattr(self.usage_calculator, 'max') else 0,
                'Q25': self.usage_calculator.first_q if hasattr(self.usage_calculator, 'first_q') else 0,
                'Q50': self.usage_calculator.second_q if hasattr(self.usage_calculator, 'second_q') else 0,
                'Q75': self.usage_calculator.third_q if hasattr(self.usage_calculator, 'third_q') else 0,
                'ModeIndex': self.usage_calculator.mode_index if hasattr(self.usage_calculator, 'mode_index') else 0
            }
        }
        logger.debug(results)
        return results
