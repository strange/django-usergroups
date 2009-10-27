from django.db import models
from usergroups.models import BaseUserGroup

class Group(BaseUserGroup):
    extra = models.CharField(max_length=200)
