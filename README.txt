Add urls::

    (r'^', include('usergroups.urls')),

Create a model that extends the BaseGroup::

    class MyGroup(BaseGroup):
        extra = models.CharField(max_length=20)

Register the model::

    options.register('groups', MyGroup)
