import datetime
import random
import sha

from django.db import models
from django.db.models import get_model
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse

from usergroups.managers import UserGroupInvitationManager

class BaseUserGroup(models.Model):
    """An abstract base class for a group of people; an association."""
    name = models.CharField(max_length=130)

    info = models.TextField(blank=True)
    website = models.URLField(blank=True)
    
    creator = models.ForeignKey(User)
    admins = models.ManyToManyField(User, related_name='admins')
    members = models.ManyToManyField(User, related_name='members')
    
    created = models.DateTimeField(default=datetime.datetime.now)
    
    def remove_admin(self, user):
        """Remove an admin from the group."""
        self.admins.remove(user)
        if user == self.creator and self.admins.count():
            # Assign a random admin to the role of being the group's creator.
            # A group can thus (if other logic allows for it) have no admins,
            # but it always has a creator.
            self.creator = self.admins.all().order_by('?')[0]
            self.save()
    
    def is_admin(self, user):
        """Test if supplied user is an admin (or the creator) of group."""
        return user in self.admins.all() or user == self.creator
    
    def save(self, *args, **kwargs):
        """Override to set add the creator as an admin and member."""
        created = self.pk is None
        super(BaseUserGroup, self).save(*args, **kwargs)
        if created:
            self.admins.add(self.creator)
            self.members.add(self.creator)
    
    def get_absolute_url(self):
        return ('usergroups.views.group_detail', (self.id, ))
    get_absolute_url = models.permalink(get_absolute_url)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        abstract = True


# First test if a custom usergroup model has been supplied. If not, create a
# subclass of BaseUserGroup.

if hasattr(settings, 'USERGROUPS_MODEL'):
    UserGroup = get_model(*settings.USERGROUPS_MODEL.split('.'))
    if UserGroup is None:
        raise ValueError(u"Custom usergroups model could not be loaded.")
else:
    class UserGroup(BaseUserGroup):
        pass

# Make sure that we're extending BaseUserGroup. (This isn't really necessary
# as we're really only interested in the save-logic and the admins m2m, but
# it's easier than checking and explaining)

if not issubclass(UserGroup, BaseUserGroup):
    raise ValueError(u"The model used in usergroups must extend BaseUserGroup.")


class UserGroupApplication(models.Model):
    """An application to join a user group."""
    user = models.ForeignKey(User)
    group = models.ForeignKey(UserGroup)
    created = models.DateTimeField(default=datetime.datetime.now)
    
    def __unicode__(self):
        return '%s applied to join %s' % (self.user.get_full_name(),
                                          self.group.name)

class UserGroupInvitation(models.Model):
    """An invitation to join a user group."""
    user = models.ForeignKey(User)
    group = models.ForeignKey(UserGroup)
    secret_key = models.CharField(max_length=30)
    created = models.DateTimeField(default=datetime.datetime.now)
    
    objects = UserGroupInvitationManager()
    
    def generate_secret_key(self):
        """Generate a secret key."""
        # Stolen from James Bennet! Oh my!
        salt = sha.new(str(random.random())).hexdigest()[:5]
        return sha.new(salt + user.username).hexdigest()
    
    def save(self, *args, **kwargs):
        if self.secret_key is None:
            self.secret_key = self.generate_secret_key()
        super(UserGroupInvitation, self).save(*args, **kwargs)