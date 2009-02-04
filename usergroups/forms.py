from django import forms
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.forms.fields import email_re
from django.conf import settings

from usergroups.models import UserGroup
from usergroups.models import EmailInvitation

class UserGroupForm(forms.ModelForm):
    """Allow a user to create and modify a user group."""
    class Meta:
        model = UserGroup
        exclude = ('members', 'admins', 'creator', 'created')


class EmailInvitationForm(forms.Form):
    """Simple form to clean multiple e-mail addresses."""
    emails = forms.CharField(widget=forms.Textarea(), required=False)
    
    def __init__(self, user, group, *args, **kwargs):
        self.user = user
        self.group = group
        super(EmailInvitationForm, self).__init__(*args, **kwargs)
    
    def parse_emails(self):
        """Parse emails and return as a list."""
        if not hasattr(self, "_emails_cache"):
            emails = self.data.has_key("emails") and self.data["emails"] or ""
            emails = emails.replace(',', ' ').replace('\n', ' ') # Remove linebreaks and commas
            self._emails_cache = [e.strip() for e in emails.split(' ') if e.strip() != ""]
        return self._emails_cache
    
    def clean_emails(self):
        """Validate all e-mail addresses."""
        emails = self.parse_emails()
        if not emails:
            raise forms.ValidationError("You haveto enter at-least one e-mail address.")
        
        for email in emails:
            if not email_re.search(email):
                raise forms.ValidationError("One or more e-mail addresses were not valid.")
        return emails
    
    def send_invitations(self):
        # TODO: Move to manager
        from django.core.urlresolvers import reverse
        if "mailer" in settings.INSTALLED_APPS:
            from mailer import send_mail
        else:
            from django.core.mail import send_mail
        current_site = Site.objects.get_current()
        
        for email in self.cleaned_data['emails']:
            invitation = EmailInvitation.objects.create(user=self.user,
                                                        group=self.group,
                                                        email=email)
            url = 'http://%s%s' % (current_site.domain,
                                   reverse('usergroups_validate_email_invitation',
                                           args=(self.group.pk,
                                                 invitation.secret_key, )))
            subject = render_to_string('usergroups/invitation_subject.txt', {
                'user': self.user,
                'site': current_site
            }).replace('\n', ' ')
            message = render_to_string('usergroups/invitation_body.txt', {
                'activation_key': invitation.secret_key,
                'site': current_site,
                'group': self.group,
                'url': url,
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
