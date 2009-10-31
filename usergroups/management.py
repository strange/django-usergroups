from django.conf import settings
from django.utils.translation import ugettext_noop as _
from django.db.models import signals

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type('usergroups_application',
                                        _("Application Received"),
                                        _("someone has applied to join a "
                                          "group"))
        notification.create_notice_type('usergroups_application_approved',
                                        _("Application Approved"),
                                        _("someone has approved an "
                                          "application to join a group"))

    signals.post_syncdb.connect(create_notice_types, sender=notification)

else:
    print "Skipping creation of NoticeTypes as notification app not found"
