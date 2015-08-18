from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect


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
