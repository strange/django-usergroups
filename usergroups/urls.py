from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'usergroups.views.group_list', name='usergroups_group_list'),
    url(r'^(?P<group_id>\d+)/$', 'usergroups.views.group_detail', name='usergroups_group_detail'),
    url(r'^create/$', 'usergroups.views.create_group', name='usergroups_create_group'),
)