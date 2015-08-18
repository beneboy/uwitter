from ..models import UserProfile


def get_user_profile(user):
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile()
        profile.user = user
        profile.save()

    return profile
