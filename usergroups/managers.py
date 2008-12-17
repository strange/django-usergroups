from django.db import models

class UserGroupInvitationManager(models.Manager):
    def handle_invite(self, user, secret_key):
        """Validate invitation key and add user to the group specified in the
        invitation. Return boolean stating whether the invitation was valid
        and processed or not.
        
        """
        try:
            invitation = self.get(user=user, secret_key=secret_key)
            invitation.group.members.add(user)
            invitation.delete()
            return True
        except self.model.DoesNotExist:
            return False