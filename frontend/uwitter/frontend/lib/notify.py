from django.contrib.auth.models import User
from .helpers import get_user_profile


def notify_of_post(poster_username):
    try:
        poster = User.objects.get_by_natural_key(poster_username)
    except User.DoesNotExist:
        return

    profile = get_user_profile(poster)

    for follower in profile.followers.all():
        print "Notifying {}".format(follower.username)