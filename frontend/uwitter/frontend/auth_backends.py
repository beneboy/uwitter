from urlparse import urljoin
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
import requests
from frontend.models import MicroServicesUser


SIGNUP_URL = urljoin(settings.MICRO_SERVICES_AUTH_URL, '/signup/')
LOGIN_URL = urljoin(settings.MICRO_SERVICES_AUTH_URL, '/login/')
USER_DETAIL_URL = urljoin(settings.MICRO_SERVICES_AUTH_URL, '/users/{}/')


class MicroServicesUserCreationForm(UserCreationForm):
    def save(self, commit=True):
        requests.post(SIGNUP_URL, data={
            'username': self.cleaned_data['username'],
            'password': self.cleaned_data['password1']
        })
        # of course you should check the response for errors here


def get_or_create_microservices_user(username, remote_id):
    try:
        u = MicroServicesUser.objects.get(remote_id=remote_id)
    except MicroServicesUser.DoesNotExist:
        u = MicroServicesUser()
        u.username = username
        u.remote_id = remote_id
        u.save()

    return u


class MicroServicesBackend(object):
    def authenticate(self, username=None, password=None):
        auth_response = requests.post(LOGIN_URL, data={'username': username, 'password': password}).json()
        if not auth_response['id']:
            return None

        return get_or_create_microservices_user(username, auth_response['id'])

    def get_user(self, user_id):
        return MicroServicesUser.objects.get(id=user_id)
