from django.views.generic import list_detail
from django.views.generic import simple
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404

from usergroups.models import UserGroup
from usergroups.models import UserGroupInvitation
from usergroups.models import UserGroupApplication
from usergroups.models import UserGroupForm

# Display views

def group_list(request, queryset=None, extra_args={}):
    if queryset is None:
        queryset = UserGroup.objects.all()
    return list_detail.object_list(request, queryset)

def group_detail(request, group_slug):
    group = get_object_or_404(UserGroup, slug=group_slug)
    return simple.direct_to_template(request, extra_context=locals(),
                                     template='groups/group_detail.html')

# Create, edit delete views

def create_group(request, form_class=UserGroupForm):
    """Create a new user group. The requesting user will be set as the
    creator (and subsequently an admin in the underlying interface).
    
    A custom form can be supplied via the ``form_class`` argument. The form
    will be fed a newly created group instance in which the creator field has
    been set. The form's ``is_valid()`` method will be called prior to save.
    
    """
    group = UserGroup(creator=request.user)
    
    if request.method == "POST":
        form = form_class(request.POST, instance=group)
        if form.is_valid():
            return HttpResponseRedirect(group.get_absolute_url())
    else:
        form = form_class(instance=group)
    return simple.direct_to_template(request, extra_context=locals(),
                                     template='usergroups/group_form.html')

@group_admin_required
def edit_group(request, group, group_slug, form_class=UserGroupForm):
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
def delete_group(request, group, group_slug):
    """Delete group."""
    group_name = group.name
    group.delete()
    return simple.direct_to_template(request,
                                     extra_context={ 'group_name': group_name },
                                     template='usergroups/group_form.html')

# Group administration views

@group_admin_required
def add_group_admin(request, group, group_slug, user_id):
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
def remove_group_admin(request, group, group_slug, user_id):
    """Remove a user's administrative privilegies in a group."""
    user = get_object_or_404(User, pk=user_id)
    group.admins.remove(user)
    return HttpResponseRedirect(group.get_absolute_url())

# Invitation/application views

@group_admin_required
def send_group_invitation(request, group, group_slug, user_id):
    """Create an invitation to a user group for a user."""
    user = get_object_or_404(User, pk=user_id)
    invitation = UserGroupInvitation.objects.create(user=user, group=group)
    return simple.direct_to_template(request, extra_context=locals(),
                                     template='groups/invitation_sent.html')

def handle_group_invitation(request, group_slug, secret_key):
    """Validates an invitation to a user group. If the credentials received
    are valid the user is added as a user in the group.
    
    """
    group = get_object_or_404(UserGroup, slug=group_slug)
    valid = UserGroupInvitation.objects.handle_invitation(request.user,
                                                          group,
                                                          secret_key)
    return simple.direct_to_template(request, extra_context=locals(),
                                     template='groups/invitation.html')

@group_admin_required
def apply_to_join_group(request, group, group_slug):
    """Allow a user to apply to join a user group."""
    already_member = group.users.filter(user=request.user).count() != 0
    if not already_member:
        UserGroupApplication.objects.create(user=request.user, group=group)
    return simple.direct_to_template(request, extra_context=locals(),
                                     template='groups/application.html')

# Helpers and decorators

def group_admin_required(view):
    """Simple decorator that makes sure that the requesting user is a member
    of the group specified by the keyword argument ``group_slug``.
    
    The actual ``UserGroup`` instance we're checking against is sent as an
    argument after the ``request`` argument to the view.
    
    """
    def decorator(request, *args, **kwargs):
        try:
            group = get_object_or_404(UserGroup, slug=kwargs['group_slug'])
            group.admins.get(pk=request.user.id)
        except User.DoesNotExist:
            return HttpResponseForbidden('You do not have administrative privilegies in this group.')
        except KeyError:
            raise
    
        return view(request, group, *args, **kwargs)
    return decorator

