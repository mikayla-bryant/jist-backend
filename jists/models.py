from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ManyToManyField
from rest_framework.relations import ManyRelatedField





class Topic(models.Model):
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

class Jist(models.Model):
    description = models.CharField(max_length=250)
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    topic = models.ForeignKey(Topic, on_delete=CASCADE, null=True)
    giphyUrl = models.URLField()
    username = models.CharField(max_length=20, null=True)

class Vote(models.Model):
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    jist = models.ForeignKey(Jist, on_delete=models.CASCADE)
    value = models.IntegerField(default=0)


