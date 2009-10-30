=================
Django Usergroups
=================

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
