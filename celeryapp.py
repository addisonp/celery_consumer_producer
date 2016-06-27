#!/usr/bin/env python

# built-ins
import os

# pip extras
from celery import Celery

app = Celery()
app.config_from_object('celery_cleanup.celeryconfig')

if __name__ == '__main__':
    app.start()
