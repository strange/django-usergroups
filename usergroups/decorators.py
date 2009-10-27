from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden

def group_admin_required(view):
    """Simple decorator that makes sure that the requesting user is a member
    of the group specified by the keyword argument ``group_id``.
    
    The actual ``UserGroup`` instance we're checking against is sent as an
    argument after the ``request`` argument to the view.
    
    """
    def decorator(request, *args, **kwargs):
        group = get_object_or_404(kwargs['model'], pk=kwargs['group_id'])
        if not group.is_admin(request.user):
            return HttpResponseForbidden('You do not have administrative privilegies in this group.')
        request.group = group 
        return view(request, *args, **kwargs)
    return decorator

