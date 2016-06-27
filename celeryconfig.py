#!/usr/bin/env python

# built-ins
import ConfigParser
from datetime import timedelta

# pip extras
from celery import signature

from kombu import Queue

# read settings.ini file, and co-erce it into a dict
config = ConfigParser.ConfigParser()
config.read(['celery_cleanup/settings.ini'])

settings_file = dict((x, dict(config.items(x))) for x in config.sections())
# the following are celery config values from settings.ini
my_settings = settings_file.get('amqp_settings', {})
'''
disney_ofe_extract_sp_settings = settings_file.get('disney_ofe_extract_sp_settings', {})
disney_ofe_restful_api_settings = settings_file.get('disney_ofe_restful_api_settings', {})
'''

BROKER_URL = my_settings.get('broker_url', 'amqp://guest:guest@localhost:5672//')
CELERY_QUEUES = (
    Queue('fox_booking_status_update', routing_key='DTDC.FOX.KRS_BOOKING_STATUS'),
)
CELERY_DEFAULT_EXCHANGE = 'fox_krs_booking_status'
CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'
CELERY_DEFAULT_ROUTING_KEY = 'DTDC.FOX.KRS_BOOKING_STATUS'

CELERY_ROUTES = {'celery_cleanup.app.task': {
    'queue':'fox_booking_status_update',
    'routing_key': 'DTDC.FOX.KRS_BOOKING_STATUS',
}}

CELERY_IMPORTS = ('celery_cleanup.tasks',)
'''
# CELERY_RESULT_BACKEND = my_settings.get('CELERY_RESULT_BACKEND', 'rpc://')
CELERY_RESULT_PERSISTENT = False
CELERY_TASK_SERIALIZER = my_settings.get('celery_task_serializer', 'json')         
CELERY_TASK_RESULT_EXPIRES = my_settings.get('celery_task_result_expires', '1800')
CELERY_RESULT_SERIALIZER  = my_settings.get('celery_result_serializer', 'json')
CELERY_TIMEZONE = my_settings.get('celery_timezone', 'America/Los_Angeles')
CELERY_ENABLE_UTC = my_settings.get('celery_enable_utc', True) 
CELERY_SHOULD_DELAY = True  # Controls if tasks should call delay() on the signature
CELERY_RESULT_PERSISTENT = False
#CELERYBEAT_SCHEDULE_FILENAME = my_settings.get('CELERYBEAT_SCHEDULE_FILENAME', '/var/ddc/celery-beat-schedule')

CELERY_IMPORTS = ('dlx_disney_ofe.tasks',)

celerybeat_schedule_settings = settings_file.get('celerybeat_schedule_settings', {})
CELERYBEAT_SCHEDULE = {
    'transfer_booking_status':{
        'task': 'dlx_disney_ofe.tasks.get_status_notifications_from_db',
        'args': (int(disney_ofe_extract_sp_settings.get('studio_id', 1101)), ),
        'kwargs': {
            'db_batch_size': int(disney_ofe_extract_sp_settings.get('db_batch_size', 10000)),
            'db_debug': int(disney_ofe_extract_sp_settings.get('db_debug', 1)),
            'chunk_size': int(disney_ofe_extract_sp_settings.get('chunk_size', 100)),
            'callbacks': [
                signature('dlx_disney_ofe.tasks.disney_api_post_notification',
                          kwargs={'post_batch_size':int(disney_ofe_restful_api_settings.get('post_batch_size', 25))},
                          should_delay=CELERY_SHOULD_DELAY),
                signature('dlx_disney_ofe.tasks.put_status_notification_to_db',
                          should_delay=CELERY_SHOULD_DELAY),
            ]
        },
        'schedule': timedelta(seconds=int(celerybeat_schedule_settings.get('interval',300)))
    },
}
'''
#CELERYD_CONCURRENCY = 4 #default to the number of cores
#CELERYD_PREFETCH_MULTIPLIER = 4
