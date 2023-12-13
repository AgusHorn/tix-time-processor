# formatter.py
# 
# November 2018
# Modified by Gaston Snaider under the course 
# "Taller de Programacion III" of the University of Buenos Aires
#


import argparse
import tarfile
import tempfile
import sys
import shutil
import os

from os import path, listdir, makedirs, unlink
from os.path import join

import logging

sys.path.insert(0, '../')
from processor.reports.report_handler import ReportHandler

logger = logging.getLogger(__name__)

def create_batch_dir(working_directory, reports_handler):
    batch_dir_name = str(reports_handler.processable_reports[0].observations[0].day_timestamp)
    batch_dir_path = join(working_directory, batch_dir_name)
    makedirs(batch_dir_path)
    for report in reports_handler.processable_reports:
        src = report.file_path
        dst = batch_dir_path
        shutil.copy(src, dst)


def reshape_results(working_directory):
    reports_handler = ReportHandler(working_directory)
    reports_handler.update_processable_reports()
    while len(reports_handler.processable_reports) > 0 and \
            reports_handler.MINIMUM_OBSERVATIONS_QTY <= reports_handler.calculate_observations_quantity(reports_handler.processable_reports):
        create_batch_dir(working_directory, reports_handler)
        reports_handler.delete_unneeded_reports()
        reports_handler.update_processable_reports()
    if len(reports_handler.processable_reports) > 0 and \
        reports_handler.calculate_observations_quantity(reports_handler.processable_reports) < reports_handler.MINIMUM_OBSERVATIONS_QTY:
        create_batch_dir(working_directory, reports_handler)
        for report in reports_handler.processable_reports:
            unlink(report.file_path)

    os.rmdir(reports_handler.failed_results_dir_path)



def parse_args(raw_args=None):
    parser = argparse.ArgumentParser(description='Script to shape the report files from the tix-time-condenser into '
                                                 'the batches. This is to imitate the way the tix-time-processor takes '
                                                 'the files and computes them by separating them into different '
                                                 'directories. The idea behind this is to use the files for '
                                                 'exploratory analysis.')
    parser.add_argument('--source_directory',
                        help='The path to the directory where the reports are.')
    parser.add_argument('--output_directory', type=str,
                        help='The name of the output directory.')
    parser.add_argument('--output_filename', '-o', action='store', default='batch-test-report.tar.gz', type=str,
                        help='The name of the output file. By default "batch-test-report.tar.gz".')
    args = parser.parse_args(raw_args)
    return args

if __name__ == "__main__":
    args = parse_args()
    logger.debug(args)
    abs_source_dir = path.abspath(args.source_directory)
    abs_output_dir = path.abspath(args.output_directory)
    output_filename = args.output_filename

    temp_dir = tempfile.mkdtemp()
    logger.info("Copying tix logs to temp dir: {}".format(temp_dir))
    source_files = listdir(abs_source_dir)
    for file in source_files:
        file_full_path = join(abs_source_dir, file)
        # Skip empty log files
        if (os.stat(file_full_path).st_size > 0):
            shutil.copy(file_full_path, temp_dir)

    logger.info("Generating batches")
    reshape_results(temp_dir)

    abs_output_file = join(abs_output_dir, output_filename)
    logger.info("Creating output TAR {}.".format(abs_output_file))
    tar = tarfile.open(abs_output_file, mode='w:gz')
    tar.add(temp_dir, arcname='')
    tar.close()
    logger.info("Output TAR successfully created.")

    logger.info("Deleting temp dir {}".format(temp_dir))
    shutil.rmtree(temp_dir)
