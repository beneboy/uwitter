import uuid
from django.conf import settings
from kombu import Connection, Exchange, Queue
from kombu.mixins import ConsumerMixin
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

    def message_request(self, request_dict, exchange):
        message_id = str(uuid.uuid4())
        request_dict['message_id'] = message_id
        self.put_message(request_dict, exchange)
        return message_id


class ResponseConsumer(ConsumerMixin):
    def __init__(self, connection, queue, receive_event):
        self.connection = connection
        self.queue = queue
        self.receive_event = receive_event
        self.received_messages = {}

    def get_consumers(self, Consumer, channel):
        return [
            Consumer(self.queue, callbacks=[self.on_message], accept=['json'])
        ]

    def on_message(self, body, message):
        self.received_messages[body['message_id']] = body['response']
        self.receive_event.set()
        self.receive_event.clear()
        message.ack()


def synchronize_message_call(consumer, wait_event, message_func, args=None, kwargs=None):
    # make an asynchronous message queue call synchronous
    args = args or []
    kwargs = kwargs or {}

    message_id = message_func(*args, **kwargs)
    while True:
        if message_id in consumer.received_messages:
            response = consumer.received_messages.pop(message_id)
            return response
        wait_event.wait()


notify_exchange, notify_queue = build_exchange_and_queue(settings.NOTIFY_QUEUE_NAME)

messages_query_exchange, messages_query_queue = build_exchange_and_queue(settings.QUERY_QUEUE_NAME)
messages_response_exchange, messages_response_queue = build_exchange_and_queue(settings.RESPONSE_QUEUE_NAME)

auth_request_exchange, auth_request_queue = build_exchange_and_queue(settings.AUTH_REQUEST_QUEUE_NAME)
auth_response_exchange, auth_response_queue = build_exchange_and_queue(settings.AUTH_RESPONSE_QUEUE_NAME)
