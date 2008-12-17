from django.shortcuts import get_object_or_404

from usergroups.models import UserGroup

def group_admin_required(view):
    """Simple decorator that makes sure that the requesting user is a member
    of the group specified by the keyword argument ``group_slug``.
    
    The actual ``UserGroup`` instance we're checking against is sent as an
    argument after the ``request`` argument to the view.
    
    """
    def decorator(request, *args, **kwargs):
        print "in deco"
        try:
            group = get_object_or_404(UserGroup, slug=kwargs['group_slug'])
            group.admins.get(pk=request.user.id)
        except User.DoesNotExist:
            return HttpResponseForbidden('You do not have administrative privilegies in this group.')
        except KeyError:
            raise
    
        return view(request, group, *args, **kwargs)
    return decorator

