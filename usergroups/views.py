from django.views.generic import list_detail
from django.views.generic import simple
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from usergroups.models import UserGroup
from usergroups.models import UserGroupInvitation
from usergroups.models import UserGroupApplication
from usergroups.forms import UserGroupForm
from usergroups.decorators import group_admin_required

# Display views

def group_list(request, queryset=None, extra_context={}):
    if queryset is None:
        queryset = UserGroup.objects.all().select_related()
    return list_detail.object_list(request, queryset)

def group_detail(request, group_id, extra_context={}):
    group = get_object_or_404(UserGroup, pk=group_id)
    return simple.direct_to_template(request, extra_context=locals(),
                                     template='usergroups/group_detail.html')

# Create, edit delete views

@login_required
def create_group(request, form_class=UserGroupForm):
    """Create a new user group. The requesting user will be set as the
    creator (and subsequently an admin in the underlying interface).
    
    A custom form can be supplied via the ``form_class`` argument. The form
    will be fed a newly created group instance in which the creator field has
    been set. The form's ``is_valid()`` method will be called prior to save.
    
    """
    instance = UserGroup(creator=request.user)
    
    if request.method == "POST":
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            new_group = form.save()
            return HttpResponseRedirect(new_group.get_absolute_url())
    else:
        form = form_class(instance=instance)
    
    return simple.direct_to_template(request, extra_context=locals(),
                                     template='usergroups/group_form.html')

@group_admin_required
def edit_group(request, group, group_id, form_class=UserGroupForm):
    """Edit an existing user group.
    
    A custom form can be supplied via the ``form_class`` argument. The form
    will be fed an existing group instance and the form's ``is_valid()``
    method will be called prior to save.
    
    """
    if request.method == "POST":
        form = form_class(request.POST, instance=group)
        if form.is_valid():
            return HttpResponseRedirect(group.get_absolute_url())
    else:
        form = form_class(instance=group)
    
    return simple.direct_to_template(request, extra_context=locals(),
                                     template='usergroups/group_form.html')

@group_admin_required
def delete_group(request, group, group_id):
    """Delete an existing group."""
    group_name = group.name
    group.delete()
    return simple.direct_to_template(request,
                                     extra_context={ 'group_name': group_name },
                                     template='usergroups/group_deleted.html')

# Group administration views

@group_admin_required
def add_group_admin(request, group, group_id, user_id):
    """Add a user to the list of users with administrative privilegies in a
    group.
    
    """
    user = get_object_or_404(User, pk=user_id)
    group.admins.add(user)
    
    # The interface should prevent this from ever being needed.
    if user not in group.users:
        group.users.add(user)
    return HttpResponseRedirect(group.get_absolute_url())

@group_admin_required
def remove_group_admin(request, group, group_id, user_id):
    """Remove a user's administrative privilegies in a group."""
    user = get_object_or_404(User, pk=user_id)
    group.admins.remove(user)
    return HttpResponseRedirect(group.get_absolute_url())

# Invitation/application views

@group_admin_required
def send_group_invitation(request, group, group_id, user_id):
    """Create an invitation to a user group for a user."""
    user = get_object_or_404(User, pk=user_id)
    invitation = UserGroupInvitation.objects.create(user=user, group=group)
    return simple.direct_to_template(request, extra_context=locals(),
                                     template='groups/invitation_sent.html')

def handle_group_invitation(request, group_id, secret_key):
    """Validates an invitation to a user group. If the credentials received
    are valid the user is added as a user in the group.
    
    """
    group = get_object_or_404(UserGroup, pk=group_id)
    valid = UserGroupInvitation.objects.handle_invitation(request.user,
                                                          group,
                                                          secret_key)
    return simple.direct_to_template(request, extra_context=locals(),
                                     template='groups/invitation.html')

@group_admin_required
def apply_to_join_group(request, group, group_id):
    """Allow a user to apply to join a user group."""
    already_member = group.users.filter(user=request.user).count() != 0
    if not already_member:
        UserGroupApplication.objects.create(user=request.user, group=group)
    return simple.direct_to_template(request, extra_context=locals(),
                                     template='groups/application.html')

# Helpers and decorators.

