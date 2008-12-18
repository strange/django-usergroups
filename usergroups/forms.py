from django import forms

from usergroups.models import UserGroup

class UserGroupForm(forms.ModelForm):
    """Allow a user to create and modify a user group."""
    class Meta:
        model = UserGroup
        exclude = ('members', 'admins', 'creator', 'created')