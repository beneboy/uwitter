from ..models import MicroServicesUser
from .helpers import get_user_profile


def notify_of_post(poster_username):
    try:
        poster = MicroServicesUser.objects.get_by_natural_key(poster_username)
    except MicroServicesUser.DoesNotExist:
        return

    profile = get_user_profile(poster)

    for follower in profile.followers.all():
        print "Notifying {}".format(follower.username)
