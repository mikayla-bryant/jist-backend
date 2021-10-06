from django.contrib import admin
from .models import Jist, Topic, Vote


admin.site.register(Jist)
admin.site.register(Vote)
admin.site.register(Topic)

# Register your models here.
