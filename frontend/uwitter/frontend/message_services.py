from datetime import datetime
from urlparse import urljoin
from django.conf import settings
import requests
from models import Uweet, MicroServicesUser


def transform_raw_dict(message_dict):
    # insert native python objects instead of string/ids in dict that comes back from ms
    return {
        'poster': MicroServicesUser.objects.get(remote_id=message_dict['user_id']),
        'date_posted': datetime.strptime(message_dict['date_posted'], "%Y-%m-%dT%H:%M:%S.%f"),
        'user_id': message_dict['user_id'],
        'id': message_dict['id'],
        'message': message_dict['message']
    }



class LocalMessageService(object):
    def post_message(self, user_id, message):
        user = MicroServicesUser.objects.get(id=user_id)

        u = Uweet()
        u.message = message
        u.poster = user
        u.save()

    def all_messages(self):
        return Uweet.objects.order_by('-date_posted')

    def user_messages(self, user_id):
        poster = MicroServicesUser.objects.get(id=user_id)
        return Uweet.objects.filter(poster=poster).order_by('-date_posted')

    def search_messages(self, search):
        return Uweet.objects.filter(message__contains=search)


class MicroServiceMessageService(object):
    @property
    def base_url(self):
        return settings.MICRO_SERVICES_MESSAGES_URL

    @property
    def post_url(self):
        return urljoin(self.base_url, '/messages/post')

    @property
    def search_url(self):
        return urljoin(self.base_url, '/messages/search')

    def get_user_message_url(self, user_id):
        return urljoin(self.base_url, '/messages/{}'.format(user_id))

    @property
    def all_messages_url(self):
        return urljoin(self.base_url, '/messages/')

    def post_message(self, user_id, message):
        user = MicroServicesUser.objects.get(id=user_id)
        requests.post(self.post_url, data={'user_id': user.remote_id, 'message': message})

    def user_messages(self, user_id):
        user = MicroServicesUser.objects.get(id=user_id)
        messages = requests.get(self.get_user_message_url(user.remote_id)).json()['messages']
        return map(transform_raw_dict, messages)

    def search_messages(self, search):
        messages = requests.get(self.search_url, params={'search': search}).json()['messages']
        return map(transform_raw_dict, messages)

    def all_messages(self):
        messages = requests.get(self.all_messages_url).json()['messages']
        return map(transform_raw_dict, messages)


def get_message_service():
    if settings.MESSAGE_SERVICE == 'local':
        return LocalMessageService()
    elif settings.MESSAGE_SERVICE == 'remote':
        return MicroServiceMessageService()
