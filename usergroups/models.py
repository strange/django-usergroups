import datetime
import hashlib
import random

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models

from usergroups.managers import EmailInvitationManager

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


class EmailInvitation(BaseGroupRelation):
    """An invitation to join a user group."""
    user = models.ForeignKey(User)
    email = models.EmailField()
    secret_key = models.CharField(max_length=30)
    created = models.DateTimeField(default=datetime.datetime.now)
    
    objects = EmailInvitationManager()
    
    def generate_secret_key(self):
        """Generate a secret key."""
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        return hashlib.sha1(salt + self.user.username).hexdigest()[:30]
    
    def save(self, *args, **kwargs):
        if not self.secret_key:
            self.secret_key = self.generate_secret_key()
        super(EmailInvitation, self).save(*args, **kwargs)
