from kombu import Connection, Exchange, Queue

QUEUE_NAME = 'uwitter_notify'

notify_exchange = Exchange(QUEUE_NAME, type='direct')
notify_queue = Queue(QUEUE_NAME, notify_exchange)


def get_connection():
    return Connection('redis://localhost:6379/')
