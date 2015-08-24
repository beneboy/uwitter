"""uwitter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url

urlpatterns = [
    url(r'^/?$', 'frontend.views.index'),
    url(r'^post/?$', 'frontend.views.post_uweet'),
    url(r'^uweets/search/?$', 'frontend.views.search_uweets'),  # conflict! can't have a user with username 'search'
    url(r'^uweets/(?P<username>\w+)/?$', 'frontend.views.user_uweets'),

    url(r'^follow/(?P<other_username>\w+)/?$', 'frontend.user_views.follow'),
    url(r'^unfollow/(?P<other_username>\w+)/?$', 'frontend.user_views.unfollow'),

    url(r'^user-uweets/?$', 'frontend.user_views.user_uweet_redirect'),
    url(r'^accounts/register/?$', 'frontend.user_views.register'),
    url(r'^accounts/', include('django.contrib.auth.urls'))
]
