# celery_consumer_producer
Example usage of celery both as a consumer and producer

```
>>> import celery_cleanup.tasks
>>> celery_cleanup.tasks.get_missing_notification_response_for_krs.apply_async(queue='fox_booking_status_update',routing_key='DTDC.FOX.KRS_BOOKING_STATUS')
```
