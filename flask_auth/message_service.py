from kombu import Connection, Exchange, Queue
from kombu.mixins import ConsumerMixin
from kombu.pools import producers
from db import process_request_message

QUERY_QUEUE_NAME = 'uwitter_auth_request'
auth_request_exchange = Exchange(QUERY_QUEUE_NAME, type='direct')
auth_request_queue = Queue(QUERY_QUEUE_NAME, auth_request_exchange)


RESPONSE_QUEUE_NAME = 'uwitter_auth_response'
auth_response_exchange = Exchange(RESPONSE_QUEUE_NAME, type='direct')
auth_response_queue = Queue(RESPONSE_QUEUE_NAME, auth_response_exchange)


class AuthResponseProducer(object):
    def __init__(self, connection, queue):
        self.connection = connection
        self.queue = queue

    def put_message(self, message, exchange):
        with producers[self.connection].acquire(block=True) as producer:
            producer.publish(message, exchange=exchange, declare=[exchange])


class AuthRequestConsumer(ConsumerMixin):
    def __init__(self, connection, queue):
        self.connection = connection
        self.queue = queue

    def get_consumers(self, Consumer, channel):
        return [
            Consumer(self.queue, callbacks=[self.on_message], accept=['json'])
        ]

    def on_message(self, body, message):
        response = process_request_message(body)

        if response is not None:
            response_prod = AuthResponseProducer(self.connection, auth_response_exchange)
            response_prod.put_message({'response': response, 'message_id': body['message_id']},
                                      auth_response_queue)
        message.ack()


def get_connection():
    return Connection('redis://localhost:6379/')


def run_service():
    conn = get_connection()
    AuthRequestConsumer(conn, auth_request_queue).run()


if __name__ == '__main__':
    run_service()
