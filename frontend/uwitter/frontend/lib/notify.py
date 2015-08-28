from ..models import MicroServicesUser
from .helpers import get_user_profile
from ..message_queue.shared import get_connection, notify_queue
from ..message_queue.notify import NotifyProducer


def notify_of_post(poster_username, post_content):
    try:
        poster = MicroServicesUser.objects.get_by_natural_key(poster_username)
    except MicroServicesUser.DoesNotExist:
        return

    profile = get_user_profile(poster)

    connection = get_connection()
    notifier = NotifyProducer(connection, notify_queue)

    for follower in profile.followers.all():
        print "Notifying {}".format(follower.username)
        notifier.notify_of_post(poster_username, follower.username, post_content)
