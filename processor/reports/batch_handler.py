import datetime
import logging
import json
import os
from os.path import join, exists, isfile, islink

from processor.reports.report import Report
from processor.reports.batch import Batch

from processor.reports.report_JSON import ReportJSON

logger = logging.getLogger(__name__)

class BatchHandler:

    def __init__(self, batches_directory):
        self.logger = logger.getChild('BatchHandler')
        self.batches_directory = batches_directory
        self.batches = list()
        self.batches_files_names = self.__get_batches_files_names()

    def __get_batches_files_names(self):
        """
        Get the batches names in the given directory

        Returns
        -------
        a list of names as strings
        """
        return [join(self.batches_directory, batch_file_name)
                for batch_file_name in sorted(os.listdir(self.batches_directory))
                if batch_file_name.endswith('.json')]
    
    def get_batches(self):
        return self.batches
    
    def load_batches_and_get_observations(self):
        """
        Loads the batches and gets the observations.
        """
        observations = []
        for batch_path in self.batches_files_names:
            new_batch = Batch().load(batch_path)
            if (len(new_batch.observations) == 0):
                self.logger.error('Batch {} has no observations. Batch skipped'.format(batch_path))
                continue
            observations.append(new_batch.observations)
            self.batches.append(new_batch)
        return observations
