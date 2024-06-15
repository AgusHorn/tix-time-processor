import datetime
import logging
import json
import os
from os.path import join, exists, isfile, islink

from processor.reports.report import Report
from processor.reports.batch import Batch

from processor.reports.report_JSON import ReportJSON

logger = logging.getLogger(__name__)

class ReportHandler:
    OBSERVATIONS_QUANTITY = 61

    FAILED_RESULTS_DIR_NAME = 'failed-results'
    FAILED_REPORT_FILE_NAME_TEMPLATE = 'failed-report-{timestamp}.json'

    CLIENT_NETSTAT_PATH = 'network_usage_torrents.log'


    @staticmethod
    def delete_reports_files(reports):
        for report in reports:
            if exists(report.file_path):
                os.unlink(report.file_path)

    def __init__(self, installation_dir_path):
        self.logger = logger.getChild('ReportHandler')
        self.installation_dir_path = installation_dir_path
        self.logger.info('Installation directory {}'.format(self.installation_dir_path))
        self.failed_results_dir_path = join(self.installation_dir_path, self.FAILED_RESULTS_DIR_NAME)
        if not exists(self.failed_results_dir_path):
            self.logger.info('Creating {} directory'.format(self.failed_results_dir_path))
            os.mkdir(self.failed_results_dir_path)
        self.reports = list()
        self.reports_files_names = self.__get_report_files_names()
        self.client_netstat_times = self.__get_client_net_stat_times()
        self.batches = list()
        self.current_netstat_index = 0

    def __get_report_files_names(self):
        """
        Get the reports names in the given directory

        Returns
        -------
        a list of names as strings
        """
        return [join(self.installation_dir_path, report_file_name)
                for report_file_name in sorted(os.listdir(self.installation_dir_path))
                if report_file_name.endswith('.json')]

    def __get_client_net_stat_times(self):
        """
        Gets the times measured by net_stat in the test.
        This net_stat file shows the actual network usage in the network.

        Returns
        -------
        a list of times as strings
        """
        times = []
        absolute_path = os.path.dirname(os.path.abspath(__file__))
        filename = absolute_path + '/network_usage_torrents.log'
        with open(filename) as netstat_file:
            # Skip header
            next(netstat_file)
            for line in netstat_file:
                time = line.split('|')[0]
                times.append(time)
        return times
    
    def save_first_batch(self, report):
        """
        Saves the first batch in order to align them with the net_stat measures.
        """
        for i in range(0, len(report.observations)):
            observation = report.observations[i]
            current_net_stat_time = int(self.client_netstat_times[self.current_netstat_index].split('.')[0])
            if observation.day_timestamp == current_net_stat_time:
                self.save_batch(report, i)

    def save_batch(self, report, index = 0):
        """
        Creates and saves the batch with the observations.
        """
        batch = Batch(report.from_dir, report.to_dir, report.observations[index].day_timestamp, report.observations[-1].day_timestamp, report.observations[index:])
        self.batches.append(batch)
        self.current_netstat_index += 1
        batch.save(self.installation_dir_path + '/' + str(report.observations[0].day_timestamp) + '.json')

    def process_reports_and_generate_batches(self):
        """
        Process the reports and generates the batches with the observations.
        """
        for i in range(0, len(self.reports_files_names)):
            if (self.current_netstat_index > len(self.client_netstat_times)):
                break
            new_report = Report.load(self.reports_files_names[i])
            self.__check_same_ip(self.reports, new_report)
            netstat_time = int(self.client_netstat_times[self.current_netstat_index].split('.')[0])
            if (new_report.observations[-1].day_timestamp < netstat_time):
                continue
            if (len(self.batches) < 1):
                # We do this to align reports with the net_stat measures
                self.save_first_batch(new_report)
            else:
                self.save_batch(new_report)
            self.reports.append(new_report)

    def __check_same_ip(self, processable_reports, new_report):
        """
        Validates that the new report has the same ip as the ones before.
        If it is not the same, then we erase all the previous reports.
        """
        if len(processable_reports) > 0:
            processable_reports_ip = processable_reports[0].from_dir.split(':')[0]
            new_report_ip = new_report.from_dir.split(':')[0]
            if new_report_ip != processable_reports_ip:
                self.delete_reports_files(processable_reports)
                processable_reports.clear()
        
    def delete_unneeded_reports(self):
        report = self.processable_reports[0]
        if exists(report.file_path):
                os.unlink(report.file_path)
        # reports_to_delete_qty = len(self.processable_reports) // 2
        # reports_to_delete = self.processable_reports[:reports_to_delete_qty]
        # self.delete_reports_files(reports_to_delete)

    def failed_results_dir_is_empty(self):
        return not exists(self.failed_results_dir_path) or len(os.listdir(self.failed_results_dir_path)) == 0

    def back_up_failed_results(self, results, ip):
        json_failed_results = {
            'results': results,
            'ip': ip
        }
        failed_result_file_name = self.FAILED_REPORT_FILE_NAME_TEMPLATE.format(timestamp=results['timestamp'])
        failed_result_file_path = join(self.failed_results_dir_path, failed_result_file_name)
        with open(failed_result_file_path, 'w') as failed_result_file:
            json.dump(json_failed_results, failed_result_file)
