import threading
from .shared import get_connection, ProducerBase, ResponseConsumer, auth_request_exchange, auth_request_queue, \
    auth_response_queue, synchronize_message_call


message_received_event = threading.Event()


class AuthRequestProducer(ProducerBase):
    def signup(self, username, password):
        return self.message_request({'action': 'signup', 'username': username, 'password': password},
                                    auth_request_exchange)

    def login(self, username, password):
        return self.message_request({'action': 'login', 'username': username, 'password': password},
                                    auth_request_exchange)

    def get_user(self, user_id):
        return self.message_request({'action': 'get_user', 'user_id': user_id}, auth_request_exchange)


auth_response_consumer = ResponseConsumer(get_connection(), auth_response_queue, message_received_event)
# a singleton


threading.Thread(target=auth_response_consumer.run).start()


def signup(username, password):
    qp = AuthRequestProducer(get_connection(), auth_request_queue)
    return synchronize_message_call(auth_response_consumer, message_received_event, qp.signup, [username, password])


def login(username, password):
    qp = AuthRequestProducer(get_connection(), auth_request_queue)
    return synchronize_message_call(auth_response_consumer, message_received_event, qp.login,
                                    [username, password])


def get_user(user_id):
    qp = AuthRequestProducer(get_connection(), auth_request_queue)
    return synchronize_message_call(auth_response_consumer, message_received_event, qp.get_user,
                                    [user_id])
