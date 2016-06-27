#!/usr/bin/env python

# Built-ins
import itertools
import logging
import sys

sys.path.append('../..')

import psycopg2
import psycopg2.extras

# pip extras
# import gevent.socket
# import grequests
# import lxml.etree
# import pymssql
# import six

from celery.contrib import rdb
from celery.utils.log import get_task_logger
from celery import signature
from foxkrs_pushBookingStatusLite import push_booking_status_lite
from foxkrs_pushBookingStatusLite import cleanup_ddc_notification_respond

from celeryconfig import settings_file

# module level imports
from celery_cleanup import celeryapp


logger = get_task_logger(__name__)
# Silence requests from telling me every time it makes a connection.
logging.getLogger("requests").setLevel(logging.DEBUG)

def handle_callback(callbacks=[]):
    '''
    A generic function that handles a list of callback functions, execute each callback in order
    :param  list(dict) callbacks: a list of celery signature objects
    '''
    if any(callbacks):
        callbacks = [signature(x) for x in callbacks]
        callbacks[0].kwargs['callbacks'] = callbacks[1:]  #Pass the rest callbacks into callbacks[0] in keyword arguments 'callbacks'
        logger.debug("Task: {0!r}".format(callbacks[0].get('task','Task name not found in handle_callback')))
        should_delay = callbacks[0].get('options',{}).get('should_delay', True)
        logger.debug("Should delay: {0!r}".format(should_delay))
        callbacks[0].delay() if should_delay else callbacks[0]()
    else:
        logger.debug("No callbacks")

class ExceptionHandler(object):
    '''
    A customized exception handler class that catchs exception raised by grequests
    '''
    def __init__(self):
        pass
 
    def callback(self, requests, exception, **kwargs):
        #rdb.set_trace()
        exc_logger = logging.getLogger(__name__)
        for exc in exception:
            exc_logger.error(exc)
        current_task = kwargs.get('current_task')
        exc_logger.error("Reinjecting task: {0!r}".format(current_task))
        current_task.args = ([r.get('item') for r in requests], )
        if 'retry_delay' in kwargs:
            current_task.options.update({
                'countdown': kwargs.get('retry_delay', 60),  # delays task to execute 60 seconds later
            })
        callbacks = kwargs.get('callbacks', [])
        callbacks.insert(0, current_task)
        handle_callback(callbacks)

grequests_exception_handler = ExceptionHandler()

# @celery_cleanup.celeryapp.app.tasks(bind=True, ignore_result=True)
@celeryapp.app.task(bind=True, ignore_result=True)
def process_krs_booking_status_lite(self, kdm_booking_id, notification_id):
    push_booking_status_lite(kdm_booking_id)
    cleanup_ddc_notification_respond(id)

@celeryapp.app.task(bind=True, ignore_result=True)
def get_missing_notification_response_for_krs(self):
    db = psycopg2.connect("dbname=%s user=%s host=%s port=%s" % ('ddcKeyGen', 'keymaster', 'db', 5432))
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = "SELECT * from ddc_notification where name = 'KDM_BOOKING_UPDATED' and param ~ E'FOX-\\\\d' and id not in (select id from ddc_notification_respond where responder = 'Fox KRS Booking Manager')"
    cursor.execute(sql)
    data = cursor.fetchall()
    for item in data:
        # populate queue
        push_booking_status_lite.apply_async(queue=settings_file.get('amqp_settings').get('queue'),
                                             routing_key=settings_file.get('amqp_settings').get('routing_key'),
                                             args=[item.get('param'), item.get('id')]
                                             )
    cursor.close()
    db.close()
            
