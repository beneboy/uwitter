from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render, redirect
from models import UserProfile


def get_user_profile(user):
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile()
        profile.user = user
        profile.save()

    return profile


def get_user_or_404(username):
    try:
        return User.objects.get_by_natural_key(username)
    except User.DoesNotExist:
        raise Http404


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for registering. You can now log in.")
            return redirect(reverse('django.contrib.auth.views.login'))
    else:
        form = UserCreationForm()
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
