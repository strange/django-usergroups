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
