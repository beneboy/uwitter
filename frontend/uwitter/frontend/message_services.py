from urlparse import urljoin
from django.conf import settings
import requests
from models import Uweet, MicroServicesUser


class LocalMessageService(object):
    def post_message(self, user_id, message):
        user = MicroServicesUser.objects.get(id=user_id)

        u = Uweet()
        u.message = message
        u.poster = user
        u.save()

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

    def post_message(self, user_id, message):
        user = MicroServicesUser.objects.get(id=user_id)
        requests.post(self.post_url, data={'user_id': user.remote_id, 'message': message})

    def user_messages(self, user_id):
        raise NotImplementedError("User uweet not ready yet.")

    def search_messages(self, search):
        messages = requests.get(self.search_url, params={'search': search}).json()['messages']
        for message in messages:
            message['poster'] = MicroServicesUser.objects.get(remote_id=message['user_id'])

        return messages


def get_message_service():
    if settings.MESSAGE_SERVICE == 'local':
        return LocalMessageService()
    elif settings.MESSAGE_SERVICE == 'remote':
        return MicroServiceMessageService()
