from django.contrib import admin

from usergroups.models import UserGroup
from usergroups.models import UserGroupApplication
from usergroups.models import UserGroupInvitation

admin.site.register(UserGroup)
admin.site.register(UserGroupApplication)