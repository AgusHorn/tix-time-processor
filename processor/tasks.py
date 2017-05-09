import traceback
from os import listdir

import logging
from celery.schedules import crontab
from os.path import join, isdir

from processor import app, REPORTS_BASE_PATH
from processor import reports
from processor import api_communication
from processor import hurst

tasks_logger = logging.getLogger(__name__)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute='*/1'),
        process_users_data.s(REPORTS_BASE_PATH),
        name='process_users_data')


@app.task
def process_installation(installation_dir_path, user_id, installation_id):
    logger = tasks_logger.getChild('process_installation')
    logger.info('installation_dir_path: {installation_dir_path}'.format(installation_dir_path=installation_dir_path))
    try:
        data = reports.get_data(installation_dir_path)
        if len(data['observations']) == 0:
            return
        results = hurst.process_observations(data['observations'])
        as_info = {
            'id': data['as_id'],
            'owner': data['as_owner']
        }
        if not api_communication.post_results(results, as_info, user_id, installation_id):
            reports.back_up_failed_results(installation_dir_path, results, as_info)
    except:
        logger.error('Error while trying to process installation {}'.format(installation_dir_path))
        logger.error('Exception caught {}'.format(traceback.format_exc()))
        raise


@app.task
def process_users_data(reports_base_path):
    logger = tasks_logger.getChild('process_users_data')
    logger.info('Processing users data')
    logger.debug('reports_base_path: {reports_base_path}'.format(reports_base_path=reports_base_path))
    for first_file in listdir(reports_base_path):
        first_file_path = join(reports_base_path, first_file)
        if isdir(first_file_path):
            user_dir_name = first_file
            user_dir_path = first_file_path
            logger.debug('user_dir_path: {user_dir_path}'.format(user_dir_path=user_dir_path))
            for second_file in listdir(user_dir_path):
                second_file_path = join(user_dir_path, second_file)
                if isdir(second_file_path):
                    installation_dir_name = second_file
                    installation_dir_path = second_file_path
                    logger.debug('installation_dir_path: {installation_dir_path}'
                                 .format(installation_dir_path=installation_dir_path))
                    process_installation.delay(installation_dir_path, user_dir_name, installation_dir_name)