from .shared import notify_exchange
from kombu.pools import producers


class NotifyProducer(object):
    def __init__(self, connection, queue):
        self.connection = connection
        self.queue = queue

    def put_message(self, message, exchange):
        with producers[self.connection].acquire(block=True) as producer:
            producer.publish(message, exchange=exchange, declare=[exchange])

    def notify_of_post(self, poster, follower, post_content):
        self.put_message({'poster': poster, 'follower': follower, 'post_content': post_content}, notify_exchange)
