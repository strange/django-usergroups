from django import forms

from usergroups.models import UserGroup

class UserGroupForm(forms.ModelForm):
    """Allow a user to create a user group."""
    def __init__(self, *args, **kwargs):
        super(UserGroupForm, self).__init__(*args, **kwargs)
        # Remove the slug-field if we're updating the group.
        if hasattr(self, 'instance'):
            del self.fields['slug']
    
    class Meta:
        model = UserGroup
        exclude = ('members', 'admins', 'creator', 'created')