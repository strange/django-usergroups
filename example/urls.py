from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

from usergroups import options

from example.groups.models import Group

class GroupConfig(options.BaseUserGroupConfiguration):
    pass

options.register('test', Group, GroupConfig)

urlpatterns = patterns('',
    (r'^', include('usergroups.urls')),
    ('^admin/', include(admin.site.urls)),
)
