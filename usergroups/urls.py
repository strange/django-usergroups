from django.conf.urls.defaults import *

p = (
    url(r'^(?P<slug>\w+)/$', 'usergroups.views.group_list',
        name='usergroups_group_list'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/$',
        'usergroups.views.group_detail', name='usergroups_group_detail'),
    
    # Members
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/leave/$',
        'usergroups.views.leave_group', name='usergroups_leave_group'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/members/(?P<user_id>\d+)/remove/$',
        'usergroups.views.remove_member', name='usergroups_remove_member'),
    
    # Invitations
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/invitations/send/$',
        'usergroups.views.create_email_invitation',
        name='usergroups_create_email_invitation'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/invitations/validate/(?P<key>.*?)/$',
        'usergroups.views.validate_email_invitation',
        name='usergroups_validate_email_invitation'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/joined/',
        'usergroups.views.group_joined', name='usergroups_group_joined'),
    
    ## Applications
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/applications/apply/$',
        'usergroups.views.apply_to_join_group',
        name='usergroups_apply_to_join'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/applications/(?P<application_id>\d+)/approve/$',
        'usergroups.views.approve_application',
        name='usergroups_approve_application'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/applications/(?P<application_id>\d+)/ignore/$',
        'usergroups.views.ignore_application',
        name='usergroups_ignore_application'),
    
    # Admins
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/admins/(?P<user_id>\d+)/add/$',
        'usergroups.views.add_admin',
        name='usergroups_add_admin'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/admins/(?P<user_id>\d+)/revoke/$',
        'usergroups.views.revoke_admin', name='usergroups_revoke_admin'),
    
    # Create, edit and delete
    url(r'^(?P<slug>\w+)/create/$', 'usergroups.views.create_group',
        name='usergroups_create_group'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/edit/$',
        'usergroups.views.edit_group', name='usergroups_edit_group'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/delete/$', 'usergroups.views.delete_group',
        name='usergroups_delete_group'),
    url(r'^(?P<slug>\w+)/group-deleted/$', 'django.views.generic.simple.direct_to_template',
        { 'template': 'usergroups/delete_group_done.html' },
        name='usergroups_delete_group_done')
)

urlpatterns = patterns('', *p)
