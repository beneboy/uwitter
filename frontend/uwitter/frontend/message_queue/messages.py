import threading
import uuid
from kombu.mixins import ConsumerMixin
from .shared import get_connection, ProducerBase, messages_query_exchange, messages_query_queue, \
    messages_response_queue, messages_response_exchange


message_received_event = threading.Event()


class MessagesQueryProducer(ProducerBase):
    def message_request(self, request_dict):
        message_id = str(uuid.uuid4())
        request_dict['message_id'] = message_id
        self.put_message(request_dict, messages_query_exchange)
        return message_id

    def all_message_request(self):
        return self.message_request({'query': 'all_messages'})

    def user_message_request(self, user_id):
        return self.message_request({'query': 'user_messages', 'user_id': user_id})

    def message_search_request(self, search_text):
        return self.message_request({'query': 'search_messages', 'search': search_text})

    def post_message(self, user_id, message):
        return self.message_request({'query': 'post_message', 'user_id': user_id, 'message': message})


class MessagesResponseConsumer(ConsumerMixin):
    def __init__(self, connection, queue):
        self.connection = connection
        self.queue = queue
        self.received_messages = {}

    def get_consumers(self, Consumer, channel):
        return [
            Consumer(self.queue, callbacks=[self.on_message], accept=['json'])
        ]

    def on_message(self, body, message):
        self.received_messages[body['message_id']] = body['response']
        message_received_event.set()
        message_received_event.clear()
        message.ack()


messages_response_consumer = MessagesResponseConsumer(get_connection(), messages_response_queue)  # a singleton


def run_response_thread():
    messages_response_consumer.run()


response_thread = threading.Thread(target=run_response_thread)
response_thread.start()


def synchronize_message_call(message_func, args=None, kwargs=None):
    # make an asynchronous message queue call synchronous
    args = args or []
    kwargs = kwargs or {}

    message_id = message_func(*args, **kwargs)
    while True:
        if message_id in messages_response_consumer.received_messages:
            response = messages_response_consumer.received_messages.pop(message_id)
            return response
        message_received_event.wait(timeout=10)


def get_all_messages():
    qp = MessagesQueryProducer(get_connection(), messages_query_queue)
    return synchronize_message_call(qp.all_message_request)


def get_user_messages(user_id):
    qp = MessagesQueryProducer(get_connection(), messages_query_queue)
    return synchronize_message_call(qp.user_message_request, [user_id])


def search_messages(search_text):
    qp = MessagesQueryProducer(get_connection(), messages_query_queue)
    return synchronize_message_call(qp.message_search_request, [search_text])


def post_message(user_id, message):
    qp = MessagesQueryProducer(get_connection(), messages_query_queue)
    return synchronize_message_call(qp.post_message, [user_id, message])
