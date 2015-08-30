from kombu import Connection, Exchange, Queue
from kombu.mixins import ConsumerMixin
from kombu.pools import producers
from db import search_messages, post_message, list_messages, list_user_messages

QUERY_QUEUE_NAME = 'uwitter_messages_query'
messages_query_exchange = Exchange(QUERY_QUEUE_NAME, type='direct')
messages_query_queue = Queue(QUERY_QUEUE_NAME, messages_query_exchange)


RESPONSE_QUEUE_NAME = 'uwittter_messages_response'
messages_response_exchange = Exchange(RESPONSE_QUEUE_NAME, type='direct')
messages_response_queue = Queue(RESPONSE_QUEUE_NAME, messages_response_exchange)


class MessageResponseProducer(object):
    def __init__(self, connection, queue):
        self.connection = connection
        self.queue = queue

    def put_message(self, message, exchange):
        with producers[self.connection].acquire(block=True) as producer:
            producer.publish(message, exchange=exchange, declare=[exchange])


class MessagesQueryConsumer(ConsumerMixin):
    def __init__(self, connection, queue):
        self.connection = connection
        self.queue = queue

    def get_consumers(self, Consumer, channel):
        return [
            Consumer(self.queue, callbacks=[self.on_message], accept=['json'])
        ]

    def on_message(self, body, message):
        response = None

        if body['query'] == 'all_messages':
            response = list_messages()
        elif body['query'] == 'user_messages':
            response = list_user_messages(body['user_id'])
        elif body['query'] == 'search_messages':
            response = search_messages(body['search'])
        elif body['query'] == 'post_message':
            response = post_message(body['user_id'], body['message'])

        if response is not None:
            response_prod = MessageResponseProducer(self.connection, messages_response_queue)
            response_prod.put_message({'response': response, 'message_id': body['message_id']},
                                      messages_response_exchange)
        message.ack()


def get_connection():
    return Connection('redis://localhost:6379/')


def run_service():
    conn = get_connection()
    MessagesQueryConsumer(conn, messages_query_queue).run()


if __name__ == '__main__':
    run_service()
