import threading
from .shared import get_connection, ProducerBase, ResponseConsumer, messages_query_exchange, messages_query_queue, \
    messages_response_queue, synchronize_message_call


message_received_event = threading.Event()


class MessagesQueryProducer(ProducerBase):
    def all_message_request(self):
        return self.message_request({'query': 'all_messages'}, messages_query_exchange)

    def user_message_request(self, user_id):
        return self.message_request({'query': 'user_messages', 'user_id': user_id}, messages_query_exchange)

    def message_search_request(self, search_text):
        return self.message_request({'query': 'search_messages', 'search': search_text}, messages_query_exchange)

    def post_message(self, user_id, message):
        return self.message_request({'query': 'post_message', 'user_id': user_id, 'message': message},
                                    messages_query_exchange)


messages_response_consumer = ResponseConsumer(get_connection(), messages_response_queue, message_received_event)
# a singleton


threading.Thread(target=messages_response_consumer.run).start()


def get_all_messages():
    qp = MessagesQueryProducer(get_connection(), messages_query_queue)
    return synchronize_message_call(messages_response_consumer, message_received_event, qp.all_message_request)


def get_user_messages(user_id):
    qp = MessagesQueryProducer(get_connection(), messages_query_queue)
    return synchronize_message_call(messages_response_consumer, message_received_event, qp.user_message_request,
                                    [user_id])


def search_messages(search_text):
    qp = MessagesQueryProducer(get_connection(), messages_query_queue)
    return synchronize_message_call(messages_response_consumer, message_received_event, qp.message_search_request,
                                    [search_text])


def post_message(user_id, message):
    qp = MessagesQueryProducer(get_connection(), messages_query_queue)
    return synchronize_message_call(messages_response_consumer, message_received_event, qp.post_message,
                                    [user_id, message])
