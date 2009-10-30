from django.conf.urls.defaults import *

from usergroups.views import dispatcher

p = (
    # List and detail
    url(r'^(?P<slug>\w+)/$', dispatcher, { 'view_name': 'group_list' },
        'usergroups_group_list'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/$', dispatcher,
        { 'view_name': 'group_detail' }, 'usergroups_group_detail'),

    # Create, edit and delete
    url(r'^(?P<slug>\w+)/create/$', dispatcher,
        { 'view_name': 'create_group' }, 'usergroups_create_group'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/edit/$', dispatcher,
        { 'view_name': 'edit_group' }, 'usergroups_edit_group'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/delete/$', dispatcher,
        { 'view_name': 'delete_group' }, 'usergroups_delete_group'),
    url(r'^(?P<slug>\w+)/group-deleted/$', dispatcher,
        { 'view_name': 'done', 'action': 'delete_done' }, 
        'usergroups_delete_group_done'),
    
    # Leave group
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/leave/$', dispatcher,
        { 'view_name': 'leave_group' }, 'usergroups_leave_group'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/left/$', dispatcher,
        { 'view_name': 'done', 'action': 'leave_group_done' },
        'usergroups_leave_group_done'),

    # Remove member
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/members/(?P<user_id>\d+)/remove/$',
        dispatcher, { 'view_name': 'remove_member' },
        'usergroups_remove_member'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/members/(?P<user_id>\d+)/removed/$',
        dispatcher, { 'view_name': 'remove_member_done' },
        'usergroups_remove_member_done'),

    # Manage admins
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/admins/(?P<user_id>\d+)/add/$',
        dispatcher, { 'view_name': 'add_admin' }, 'usergroups_add_admin'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/admins/(?P<user_id>\d+)/add/done/$',
        dispatcher, { 'view_name': 'add_admin_done' },
        'usergroups_add_admin_done'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/admins/(?P<user_id>\d+)/remove/$',
        dispatcher, { 'view_name': 'revoke_admin' },
        'usergroups_revoke_admin'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/admins/(?P<user_id>\d+)/removed/$',
        dispatcher, { 'view_name': 'revoke_admin_done' },
        'usergroups_revoke_admin_done'),
    
    # Invitations
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/invitations/send/$',
        dispatcher, { 'view_name': 'create_email_invitation' },
        'usergroups_create_email_invitation'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/invitations/done/', dispatcher,
        { 'view_name': 'done', 'action': 'email_invitation_done' },
        'usergroups_email_invitation_done'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/invitations/validate/(?P<key>.*?)/$',
        dispatcher, { 'view_name': 'validate_email_invitation' },  
        'usergroups_validate_email_invitation'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/joined/', dispatcher,
        { 'view_name': 'done', 'action': 'group_joined' },
        'usergroups_group_joined'),
    
    # Applications
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/applications/apply/$',
        dispatcher, { 'view_name': 'apply_to_join_group' },
        'usergroups_apply_to_join'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/applications/failed/$',
        dispatcher, { 'view_name': 'done', 'action': 'application_failed' },
        'usergroups_application_failed'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/applications/sent/$',
        dispatcher, { 'view_name': 'done', 'action': 'application_sent' },
        'usergroups_application_sent'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/applications/(?P<application_id>\d+)/approve/$',
        dispatcher, { 'view_name': 'approve_application' },  
        'usergroups_approve_application'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/applications/approved/$',
        dispatcher, { 'view_name': 'done', 'action': 'application_approved' },
        'usergroups_application_approved'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/applications/(?P<application_id>\d+)/ignore/$',
        dispatcher, { 'view_name': 'ignore_application' },  
        'usergroups_ignore_application'),
    url(r'^(?P<slug>\w+)/(?P<group_id>\d+)/applications/ignored/$',
        dispatcher, { 'view_name': 'done', 'action': 'application_ignored' },
        'usergroups_application_ignored'),
)

urlpatterns = patterns('', *p)
