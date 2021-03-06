from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render, redirect
from frontend.models import MicroServicesUser
from .lib.helpers import get_user_profile
from .auth_backends import MicroServicesUserCreationForm


def get_user_or_404(username):
    try:
        return MicroServicesUser.objects.get_by_natural_key(username)
    except MicroServicesUser.DoesNotExist:
        raise Http404


def register(request):
    if request.method == 'POST':
        form = MicroServicesUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for registering. You can now log in.")
            return redirect(reverse('django.contrib.auth.views.login'))
    else:
        form = MicroServicesUserCreationForm()
    return render(request, "registration/register.html", {
        'form': form,
    })


@login_required
def user_uweet_redirect(request):
    return redirect('frontend.views.user_uweets', username=request.user.username)


@login_required
def follow(request, other_username):
    other_user = get_user_or_404(other_username)
    profile = get_user_profile(other_user)
    profile.followers.add(request.user)
    profile.save()
    messages.success(request, "You are now following {}".format(other_username))
    return redirect(request.GET.get('return') or user_uweet_redirect)


@login_required
def unfollow(request, other_username):
    other_user = get_user_or_404(other_username)
    profile = get_user_profile(other_user)
    profile.followers.remove(request.user)
    profile.save()
    messages.success(request, "You are no longer following {}".format(other_username))
    return redirect(request.GET.get('return') or user_uweet_redirect)
