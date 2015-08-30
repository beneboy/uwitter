import json
import socket
from urlparse import urljoin
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
import requests
from frontend.models import MicroServicesUser
import message_queue.auth


SIGNUP_URL = urljoin(settings.MICRO_SERVICES_AUTH_URL, '/signup/')
LOGIN_URL = urljoin(settings.MICRO_SERVICES_AUTH_URL, '/login/')
USER_DETAIL_URL = urljoin(settings.MICRO_SERVICES_AUTH_URL, '/users/{}/')


def get_or_create_microservices_user(username, remote_id):
    try:
        u = MicroServicesUser.objects.get(remote_id=remote_id)
    except MicroServicesUser.DoesNotExist:
        u = MicroServicesUser()
        u.username = username
        u.remote_id = remote_id
        u.save()

    return u


class MicroServicesBase(object):
    def get_user(self, user_id):
        return MicroServicesUser.objects.get(id=user_id)


class MicroServicesBackend(MicroServicesBase):
    def authenticate(self, username=None, password=None):
        auth_response = requests.post(LOGIN_URL, data={'username': username, 'password': password}).json()
        if not auth_response['id']:
            return None

        return get_or_create_microservices_user(username, auth_response['id'])


class MicroServicesQueueBackend(MicroServicesBase):
    def authenticate(self, username=None, password=None):
        auth_response = message_queue.auth.login(username, password)

        if not auth_response['id']:
            return None

        return get_or_create_microservices_user(username, auth_response['id'])


def get_message_length(conn):
    length_bytes = conn.recv(4)
    return int(length_bytes)


def recv_json_message(conn):
    message_length = get_message_length(conn)

    if message_length == 0:
        return None

    json_message = ''
    while len(json_message) < message_length:
        json_message += conn.recv(message_length - len(json_message))

    message = json.loads(json_message)
    return message


def send_json_message(conn, message):
    message_json = json.dumps(message)
    conn.sendall('{:04}'.format(len(message_json)))
    # 4 bytes for the length of the data, hopefully less than 9999 chars. keeping it simple with ascii and JSON
    conn.sendall(message_json)


def connect_and_send_socket_microservices_message(message):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(settings.MICRO_SERVICES_AUTH_SOCKET)
    send_json_message(s, message)
    response = recv_json_message(s)
    s.close()
    return response


class MicroServicesSocketBackend(MicroServicesBase):
    def authenticate(self, username=None, password=None):
        auth_response = connect_and_send_socket_microservices_message(
            {'action': 'login', 'username': username, 'password': password})

        if not auth_response['id']:
            return None

        return get_or_create_microservices_user(username, auth_response['id'])


class MicroServicesUserCreationForm(UserCreationForm):
    def save_http_microservices_user(self):
        requests.post(SIGNUP_URL, data={
            'username': self.cleaned_data['username'],
            'password': self.cleaned_data['password1']
        })
        # of course you should check the response for errors here

    def save_message_queue_microservices_user(self):
        message_queue.auth.signup(self.cleaned_data['username'], self.cleaned_data['password1'])

    def save_socket_microservices_user(self):
        connect_and_send_socket_microservices_message(
            {'action': 'signup', 'username': self.cleaned_data['username'], 'password': self.cleaned_data['password1']})

    def save(self, commit=True):
        auth_backend_class = settings.AUTHENTICATION_BACKENDS[0].split('.')[-1]  # dodgy, but easy way to get class name
        if auth_backend_class == 'MicroServicesBackend':
            self.save_http_microservices_user()
        elif auth_backend_class == 'MicroServicesQueueBackend':
            self.save_message_queue_microservices_user()
        elif auth_backend_class == 'MicroServicesSocketBackend':
            self.save_socket_microservices_user()
