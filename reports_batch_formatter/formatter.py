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
from processor.reports.new_report_handler import ReportHandler

logger = logging.getLogger(__name__)

def copy_long_packets_to_tmp_directory(source_dir):
    temp_dir = tempfile.mkdtemp()
    logger.info("Copying tix logs to temp dir: {}".format(temp_dir))
    for file in listdir(source_dir):
        file_full_path = join(source_dir, file)
        # Skip empty log files
        if (os.stat(file_full_path).st_size > 0):
            shutil.copy(file_full_path, temp_dir)
    return temp_dir

def generate_batches(working_directory, source_dir):
    logger.info("Generating batches")
    reports_handler = ReportHandler(working_directory, source_dir)
    reports_handler.process_reports_and_generate_batches()
    os.rmdir(reports_handler.failed_results_dir_path)


def create_tar_file(output_dir, filename, temp_dir):
    abs_output_file = join(output_dir, filename)
    logger.info("Creating output TAR {}.".format(abs_output_file))
    tar = tarfile.open(abs_output_file, mode='w:gz')
    tar.add(temp_dir, arcname='')
    tar.close()
    logger.info("Output TAR successfully created.")


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

    temp_dir = copy_long_packets_to_tmp_directory(abs_source_dir)
    
    generate_batches(temp_dir, abs_source_dir)

    create_tar_file(abs_output_dir, output_filename, temp_dir)
    
    logger.info("Deleting temp dir {}".format(temp_dir))
    shutil.rmtree(temp_dir)
