from django import http

from usergroups import options

def dispatcher(request, slug, view_name, *args, **kwargs):
    """Dispatcher that loads configuration corresponding to `slug` and
    dispatches view corresponding to `view_name` on said configuration.

    The configuration will be added to the `extra_context` attribute of
    all dispatched views.
    
    """
    try:
        conf = options.get(slug)
        view = getattr(conf, view_name)
    except (options.ConfigurationNotRegistered, AttributeError):
        raise http.Http404

    # TODO: It might be a better idea to add the configuration to context in
    # the configuration class itself to ensure it's available.
    extra_context = kwargs.get('extra_context', {})
    extra_context.update({ 'group_config': conf })
    kwargs['extra_context'] = extra_context

    return view(request, *args, **kwargs)
