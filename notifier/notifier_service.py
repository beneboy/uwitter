from kombu import Connection, Exchange, Queue
from kombu.mixins import ConsumerMixin

QUEUE_NAME = 'uwitter_notify'

class NotifierConsumer(ConsumerMixin):
    def __init__(self, connection, queue):
        self.connection = connection
        self.queue = queue

    def get_consumers(self, Consumer, channel):
        return [
            Consumer(self.queue, callbacks=[self.on_message], accept=['json'])
        ]

    def on_message(self, body, message):
        print "Received Message: %r" % body
        message.ack()


def get_connection():
   return Connection('redis://localhost:6379/')


def run_service():
    conn = get_connection()
    notify_exchange = Exchange(QUEUE_NAME, type='direct')
    notify_queue = Queue(QUEUE_NAME, notify_exchange)
    NotifierConsumer(conn, notify_queue).run()
    

if __name__ == '__main__':
    run_service()

