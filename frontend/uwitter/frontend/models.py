from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Uweet(models.Model):
    message = models.TextField(max_length=141)
    poster = models.ForeignKey(User)
    date_posted = models.DateTimeField(auto_now_add=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    followers = models.ManyToManyField(User, related_name='following')
