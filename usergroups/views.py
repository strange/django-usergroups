from django import http

from usergroups import options

def dispatcher(request, slug, view_name, *args, **kwargs):
    try:
        conf = options.get(slug)
        view = getattr(conf, view_name)
    except (options.ConfigurationNotRegistered, AttributeError):
        raise http.Http404

    extra_context = kwargs.get('extra_context', {})
    extra_context.update({ 'group_config': conf })
    kwargs['extra_context'] = extra_context

    return view(request, *args, **kwargs)

# Convenience functions (views can be run directly using the dispatcher
# function).

def group_list(request, slug, *args, **kwargs):
    return dispatcher(request, slug, 'group_list', *args, **kwargs)

def group_detail(request, slug, *args, **kwargs):
    return dispatcher(request, slug, 'group_detail', *args, **kwargs)

def create_group(request, slug, *args, **kwargs):
    return dispatcher(request, slug, 'create_group', *args, **kwargs)

def delete_group(request, slug, *args, **kwargs):
    return dispatcher(request, slug, 'delete_group', *args, **kwargs)

def revoke_admin(request, slug, *args, **kwargs):
    return dispatcher(request, slug, 'revoke_admin', *args, **kwargs)

def leave_group(request, slug, *args, **kwargs):
    return dispatcher(request, slug, 'leave_group', *args, **kwargs)

def create_email_invitation(request, slug, *args, **kwargs):
    return dispatcher(request, slug, 'create_email_invitation', *args,
                      **kwargs)

def validate_email_invitation(request, slug, *args, **kwargs):
    return dispatcher(request, slug, 'validate_email_invitation', *args,
                      **kwargs)

def group_joined(request, slug, *args, **kwargs):
    return dispatcher(request, slug, 'group_joined', *args, **kwargs)

def remove_member(request, slug, *args, **kwargs):
    return dispatcher(request, slug, 'remove_member', *args, **kwargs)

def apply_to_join_group(request, slug, *args, **kwargs):
    return dispatcher(request, slug, 'apply_to_join_group', *args, **kwargs)

def ignore_application(request, slug, *args, **kwargs):
    return dispatcher(request, slug, 'ignore_application', *args, **kwargs)

def approve_application(request, slug, *args, **kwargs):
    return dispatcher(request, slug, 'approve_application', *args, **kwargs)

def add_admin(request, slug, *args, **kwargs):
    return dispatcher(request, slug, 'add_admin', *args, **kwargs)

def revoke_admin(request, slug, *args, **kwargs):
    return dispatcher(request, slug, 'revoke_admin', *args, **kwargs)
