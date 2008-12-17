from django.views.generic import list_detail
from django.views.generic import simple
from django.shortcuts import get_object_or_404

from usergroups.models import UserGroup
from usergroups.models import UserGroupInvitation
from usergroups.models import UserGroupApplication

# Display views

def usergroup_list(request):
    pass

def usergroup_detail(request, usergroup_slug):
    pass

# Create, edit delete views

def create_usergroup(request):
    pass

@group_admin_required
def edit_usergroup(request, group, usergroup_slug):
    pass

@group_admin_required
def delete_usergroup(request, group, usergroup_slug):
    pass

# Group administration views

@group_admin_required
def add_usergroup_admin(request, group, usergroup_slug, user_id):
    pass

@group_admin_required
def remove_usergroup_admin(request, group, usergroup_slug, user_id):
    pass

# Invitation/application views

@group_admin_required
def send_group_invitation(request, group, usergroup_slug, user_id):
    """Create an invitation to a user group for a user."""
    user = get_object_or_404(User, pk=user_id)
    invitation = UserGroupInvitation.objects.create(user=user, group=group)
    return simple.direct_to_template(request, extra_context=locals(),
                                     template='usergroups/invitation_sent.html')

def handle_group_invitation(request, usergroup_slug, secret_key):
    """Handle an invitation to a user group."""
    group = get_object_or_404(UserGroup, slug=usergroup_slug)
    valid = UserGroupInvitation.objects.handle_invitation(request.user,
                                                          group,
                                                          secret_key)
    return simple.direct_to_template(request, extra_context=locals(),
                                     template='usergroups/invitation.html')

@group_admin_required
def apply_to_join_group(request, group, usergroup_slug):
    """Allow a user to apply to join a user group."""
    already_member = group.users.filter(user=request.user).count() != 0
    if not already_member:
        UserGroupApplication.objects.create(user=request.user, group=group)
    return simple.direct_to_template(request, extra_context=locals(),
                                     template='usergroups/application.html')

# Helpers and decorators

def group_admin_required(view):
    """Simple decorator that makes sure that the requesting user is a member
    of the group specified by the keyword argument ``usergroup_slug``.
    
    The actual ``UserGroup`` instance we're checking against is sent as an
    argument after the ``request`` argument to the view.
    
    """
    def decorator(request, *args, **kwargs):
        try:
            group = get_object_or_404(UserGroup, slug=kwargs['usergroup_slug'])
            group.admins.get(pk=request.user.id)
        except User.DoesNotExist:
            return HttpResponseForbidden('Wrong API key')            
        except KeyError:
            return HttpResponseForbidden('Wrong API key')
    
        return view(request, group, *args, **kwargs)
    return decorator

