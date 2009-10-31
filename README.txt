=================
Django Usergroups
=================

A simple application that adds basic, albeit extensible, functionality to
manage groups of users in a project.

Disclaimer
==========

This is a total rewrite of my ancient reusable group app. There are several
kinks that I have not yet worked out. I will be modifying my old projects to
support this application. There might be some backwards incompatible changes
to this application as well (class-, module- and attribute name  changes,
modified views, URL layout changes, improved way to register configs etc).

Installation and configuration
==============================

Add ``usergroups`` to ``INSTALLED_APPS`` in your project's settings module.

Add urls::

    (r'^', include('usergroups.urls')),

Create a model that extends the BaseGroup::

    class MyGroup(BaseGroup):
        extra = models.CharField(max_length=20)

Register the model::

    options.register('groups', MyGroup)

A list of groups should then be available at::

    /groups/

You can override default behaviour and settings by extending
``options.BaseUserGroupConfiguration`` (see ``options.py`` for details)::

    class MyConfig(options.BaseUserGroupConfiguration):
        paginate_members_by = 35

        list_template_name = 'my_list_template.html'

        def get_create_group_form(self):
            return MyGroupForm

And register the configuration::

    options.register('groups', MyGroup, MyConfig)

Examples
========

There are some non-exhaustive examples in the application `example` located in
the root directory of the repository.
