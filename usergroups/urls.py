from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'usergroups.views.group_list', name='usergroups_group_list'),
    url(r'^(?P<group_id>\d+)/$', 'usergroups.views.group_detail',
        name='usergroups_group_detail'),
    
    # Invitations
    url(r'^(?P<group_id>\d+)/invitations/create/(?P<user_id>\d+)/$',
        'usergroups.views.invite_user', name='usergroups_invite_user'),
    
    # Applications
    url(r'^(?P<group_id>\d+)/applications/apply/$',
        'usergroups.views.apply_to_join_group',
        name='usergroups_apply_to_join'),
    url(r'^(?P<group_id>\d+)/applications/(?P<application_id>\d+)/approve/$',
        'usergroups.views.approve_application',
        name='usergroups_approve_application'),
    
    # Admins
    url(r'^(?P<group_id>\d+)/admins/(?P<user_id>\d+)/add/$',
        'usergroups.views.add_admin',
        name='usergroups_add_admin'),
    url(r'^(?P<group_id>\d+)/admins/(?P<user_id>\d+)/revoke/$',
        'usergroups.views.revoke_admin',
        name='usergroups_revoke_admin'),
    
    # Create, edit and delete
    url(r'^create/$', 'usergroups.views.create_group',
        name='usergroups_create_group'),
)