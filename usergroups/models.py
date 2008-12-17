import datetime

from django.db import models
from django.db.models import get_model
from django.contrib.auth.models import User
from django.conf import settings

class BaseUserGroup(models.Model):
    """An abstract base class for a group of people; an association."""
    name = models.CharField(max_length=130)
    slug = models.SlugField()

    info = models.TextField(blank=True)
    website = models.URLField(blank=True)
    
    creator = models.ForeignKey(User)
    admins = models.ManyToManyField(User, related_name='admins')
    members = models.ManyToManyField(User, related_name='members')
    
    created = models.DateTimeField(default=datetime.datetime.now)
    
    def user_is_admin(self, user):
        """Test if supplied user is an admin of group."""
        return user in self.admins
    
    def save(self, *args, **kwargs):
        created = False
        if not self.pk:
            created = True
        super(BaseUserGroup, self).save(*args, **kwargs)
        if created:
            self.admins.add(self.user)


class UserGroupApplication(models.Model):
    """An application to join a user group."""
    user = models.ForeignKey(User)
    usergroup = models.ForeignKey('UserGroup')


class UserGroupInvitation(models.Model):
    """An invitation to join a user group."""
    user = models.ForeignKey(User)
    usergroup = models.ForeignKey('UserGroup')
    secret_key = models.CharField(max_length=30)
    

# First test if a custom usergroup model has been supplied. If not, create a
# subclass of BaseUserGroup.

if hasattr(settings, 'USERGROUPS_MODEL'):
    UserGroup = get_model(*getattr(settings, 'USERGROUPS_MODEL').split('.'))
    if UserGroup is None:
        raise ValueError(u"Custom usergroups model could not be loaded.")
else:
    class UserGroup(BaseUserGroup):
        pass

# Make sure that we're extending BaseUserGroup. (This isn't really necessary
# as we're really only interested in the slug-field and save-logic, but it's
# easier than checking and explaining)

if not issubclass(UserGroup, BaseUserGroup):
    raise ValueError(u"The model used in usergroups must extend BaseUserGroup.")
