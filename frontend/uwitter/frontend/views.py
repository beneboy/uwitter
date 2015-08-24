from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import render, redirect
from forms import PostForm
from lib.notify import notify_of_post
from message_services import get_message_service
from models import Uweet


def index(request):
    uweets = Uweet.objects.order_by('-date_posted')

    return render(request, 'uweet_list.html', {'uweets': uweets})


@login_required
def post_uweet(request):
    if request.method == 'POST':
        post_form = PostForm(request.POST)
        if post_form.is_valid():
            ms = get_message_service()
            ms.post_message(request.user.id, post_form.cleaned_data['message'])
            notify_of_post(request.user.username)
            messages.success(request, "You have Uweeted, sweet!")
            return redirect('frontend.views.user_uweets', username=request.user.username)
    else:
        post_form = PostForm()

    return render(request, 'post.html', {'post_form': post_form})


def user_uweets(request, username):
    try:
        poster = User.objects.get_by_natural_key(username)
    except User.DoesNotExist:
        raise Http404

    ms = get_message_service()
    uweets = ms.user_messages(poster.id)

    return render(request, 'uweet_list.html', {'poster': poster, 'uweets': uweets})


def search_uweets(request):
    ms = get_message_service()
    uweets = ms.search_messages(request.GET.get('search', ''))
    return render(request, 'uweet_list.html', {'uweets': uweets})
