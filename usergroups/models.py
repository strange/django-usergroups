import datetime
import random
import sha

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import get_model

from usergroups.managers import UserGroupInvitationManager

class BaseUserGroup(models.Model):
    """An abstract base class for a group of people; an association."""
    name = models.CharField(max_length=130)

    info = models.TextField(blank=True)
    website = models.URLField(blank=True)
    
    creator = models.ForeignKey(User)
    admins = models.ManyToManyField(User, related_name='admin_of_groups')
    members = models.ManyToManyField(User, related_name='member_of_groups')
    
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
        return user == self.creator or user in self.admins.all()
    
    def save(self, *args, **kwargs):
        """Override to set add the creator as an admin and member."""
        created = self.pk is None
        super(BaseUserGroup, self).save(*args, **kwargs)
        if created:
            self.admins.add(self.creator)
            self.members.add(self.creator)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        abstract = True


class BaseGroupRelation(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()

    group = generic.GenericForeignKey()

    class Meta:
        abstract = True


class UserGroupApplication(BaseGroupRelation):
    """An application to join a user group."""
    user = models.ForeignKey(User)
    created = models.DateTimeField(default=datetime.datetime.now)
    
    def __unicode__(self):
        return '%s applied to join %s' % (self.user.get_full_name(),
                                          self.group.name)

class UserGroupInvitation(BaseGroupRelation):
    """An invitation to join a user group."""
    user = models.ForeignKey(User)
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


class EmailInvitation(BaseGroupRelation):
    """An invitation to join a user group."""
    user = models.ForeignKey(User)
    email = models.EmailField()
    secret_key = models.CharField(max_length=30)
    created = models.DateTimeField(default=datetime.datetime.now)
    
    objects = UserGroupInvitationManager()
    
    def generate_secret_key(self):
        """Generate a secret key."""
        # Stolen from James Bennet! Oh my!
        salt = sha.new(str(random.random())).hexdigest()[:5]
        return sha.new(salt + self.user.username).hexdigest()[:30]
    
    def save(self, *args, **kwargs):
        if not self.secret_key:
            self.secret_key = self.generate_secret_key()
        super(EmailInvitation, self).save(*args, **kwargs)
