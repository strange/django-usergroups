from django.test.client import Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from usergroups.options import BaseUserGroupConfiguration
from usergroups import options
from usergroups.models import EmailInvitation
from usergroups.models import UserGroupApplication

from example.groups.models import Group

tests = """
>>> u1 = User.objects.create_user(username='admin', password='admin',
...                               email='admin@example.com')
>>> u2 = User.objects.create_user(username='user', password='user',
...                               email='user@example.com')

>>> c1 = Client()
>>> c1.login(username='admin', password='admin')
True
>>> c2 = Client()
>>> c2.login(username='user', password='user')
True
>>> c3 = Client()

# Create a test-group
>>> g = Group.objects.create(creator=u1, name='group')

>>> assert(g.admins.count() == 1)
>>> assert(g.members.count() == 1)

# Test views

# List groups
>>> r = get(c1, 'usergroups_group_list', { 'slug': 'test' })
>>> r.status_code
200

# Create group
>>> r = get(c3, 'usergroups_create_group', { 'slug': 'test' })
>>> r.status_code
302
>>> r['location']
'http://testserver/accounts/login/?next=/test/create/'

>>> r = get(c1, 'usergroups_create_group', { 'slug': 'test' })
>>> r.status_code
200

>>> data = { 'name': 'test', 'extra': 'extra data' }
>>> r = post(c1, 'usergroups_create_group', data, { 'slug': 'test' })
>>> r.status_code
302

# Detail
>>> r = get(c1, 'usergroups_group_detail',
...         { 'slug': 'test', 'group_id': g.pk })
>>> r.status_code
200

# Email invitations
>>> g.members.count()
1

>>> r = get(c2, 'usergroups_create_email_invitation',
...         { 'slug': 'test', 'group_id': g.pk })
>>> r.status_code # user w/o administrative privileges
400

>>> r = get(c1, 'usergroups_create_email_invitation',
...         { 'slug': 'test', 'group_id': g.pk })
>>> r.status_code
200

>>> r = post(c1, 'usergroups_create_email_invitation',
...          { 'emails': u2.email },
...          { 'slug': 'test', 'group_id': g.pk, })
>>> r.status_code
302

>>> invitation = EmailInvitation.objects.get(email=u2.email)

>>> r = get(c2, 'usergroups_validate_email_invitation',
...         { 'slug': 'test', 'group_id': g.pk, 'key': 'erroneous_key' })
>>> r.status_code
200

>>> r = get(c2, 'usergroups_validate_email_invitation',
...         { 'slug': 'test', 'group_id': g.pk, 'key': invitation.secret_key })
>>> r.status_code
302

>>> g.members.count()
2

# Members
>>> r = post(c2, 'usergroups_leave_group', {},
...          { 'slug': 'test', 'group_id': g.pk })
>>> r.status_code
302

>>> g.members.count()
1

>>> g.members.add(u2)

>>> r = post(c2, 'usergroups_remove_member', {},
...          { 'slug': 'test', 'group_id': g.pk, 'user_id': u2.pk })
>>> r.status_code # user w/o administrative privileges
400

>>> r = post(c1, 'usergroups_remove_member',
...          {},
...          { 'slug': 'test', 'group_id': g.pk, 'user_id': u2.pk })
>>> r.status_code
302

>>> g.members.count()
1

# Applications
>>> r = post(c2, 'usergroups_apply_to_join', {},
...          { 'slug': 'test', 'group_id': g.pk })
>>> r.status_code
302

>>> application = UserGroupApplication.objects.get(pk=1)

>>> r = post(c2, 'usergroups_ignore_application', {},
...          { 'slug': 'test', 'group_id': g.pk, 'application_id': application.pk })
>>> r.status_code # user w/o administrative privileges
400

>>> r = post(c1, 'usergroups_ignore_application', {},
...          { 'slug': 'test', 'group_id': g.pk, 'application_id': application.pk })
>>> r.status_code
302

>>> r = post(c2, 'usergroups_apply_to_join', {},
...          { 'slug': 'test', 'group_id': g.pk })
>>> r.status_code
302

>>> application = UserGroupApplication.objects.get(pk=1)

>>> r = post(c1, 'usergroups_approve_application', {},
...          { 'slug': 'test', 'group_id': g.pk, 'application_id': application.pk })
>>> r.status_code
302

# Admins

>>> r = get(c1, 'usergroups_add_admin',
...         { 'slug': 'test', 'group_id': g.pk, 'user_id': u2.pk })
>>> r.status_code
200

>>> r = post(c2, 'usergroups_add_admin', {},
...          { 'slug': 'test', 'group_id': g.pk, 'user_id': u2.pk })
>>> r.status_code
400

>>> r = post(c1, 'usergroups_add_admin', {},
...          { 'slug': 'test', 'group_id': g.pk, 'user_id': u2.pk })
>>> r.status_code
302

>>> g.admins.count()
2

>>> r = post(c1, 'usergroups_revoke_admin', {},
...          { 'slug': 'test', 'group_id': g.pk, 'user_id': u2.pk })
>>> r.status_code
302

>>> r = post(c2, 'usergroups_revoke_admin', {},
...          { 'slug': 'test', 'group_id': g.pk, 'user_id': u2.pk })
>>> r.status_code
400

# Edit group
>>> g.admins.count()
1

>>> g.name
'group'

>>> r = post(c2, 'usergroups_edit_group',
...          { 'name': 'Group', 'extra': 'extra stuff' },
...          { 'slug': 'test', 'group_id': g.pk })
>>> r.status_code
400

>>> r = post(c1, 'usergroups_edit_group',
...          { 'name': 'Group', 'extra': 'extra stuff' },
...          { 'slug': 'test', 'group_id': g.pk })
>>> r.status_code
302

>>> g = Group.objects.get(pk=1)
>>> g.name
u'Group'

# Delete group
>>> r = get(c1, 'usergroups_delete_group',
...         { 'slug': 'test', 'group_id': g.pk })
>>> r.status_code
200

>>> r = post(c2, 'usergroups_delete_group', {},
...          { 'slug': 'test', 'group_id': g.pk })
>>> r.status_code
400

>>> r = post(c1, 'usergroups_delete_group', {},
...          { 'slug': 'test', 'group_id': g.pk })
>>> r.status_code
302

>>> Group.objects.count()
1


# TEST: Auto assign creator and admins.
# TEST: JSON responses.

"""

def get(client, view_name, kwargs={}):
    url = reverse(view_name, kwargs=kwargs)
    return client.get(url)

def post(client, view_name, data, kwargs={}):
    url = reverse(view_name, kwargs=kwargs)
    return client.post(url, data)

__test__ = { 'doctest': tests }
