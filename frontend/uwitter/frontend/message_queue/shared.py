from django.conf import settings
from kombu import Connection, Exchange, Queue
from kombu.pools import producers


def build_exchange_and_queue(queue_name):
    exchange = Exchange(queue_name, type='direct')
    queue = Queue(queue_name, exchange)
    return exchange, queue


def get_connection():
    return Connection('redis://localhost:6379/')


class ProducerBase(object):
    def __init__(self, connection, queue):
        self.connection = connection
        self.queue = queue

    def put_message(self, message, exchange):
        with producers[self.connection].acquire(block=True) as producer:
            producer.publish(message, exchange=exchange, declare=[exchange])


notify_exchange, notify_queue = build_exchange_and_queue(settings.NOTIFY_QUEUE_NAME)
messages_query_exchange, messages_query_queue = build_exchange_and_queue(settings.QUERY_QUEUE_NAME)
messages_response_exchange, messages_response_queue = build_exchange_and_queue(settings.RESPONSE_QUEUE_NAME)
