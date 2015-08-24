from django.conf import settings
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


def get_message_service():
    if settings.MESSAGE_SERVICE == 'local':
        return LocalMessageService()