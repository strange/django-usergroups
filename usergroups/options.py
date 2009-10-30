from django import http
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms.models import modelform_factory
from django.shortcuts import get_object_or_404
from django.utils import simplejson
from django.views.generic import list_detail
from django.views.generic.simple import direct_to_template

from usergroups.decorators import group_admin_required
from usergroups.forms import EmailInvitationForm
from usergroups.models import BaseUserGroup
from usergroups.models import EmailInvitation
from usergroups.models import UserGroupApplication

if "notification" in settings.INSTALLED_APPS and \
   hasattr(settings, 'USERGROUPS_SEND_NOTIFICATIONS') and \
   settings.USERGROUPS_SEND_NOTIFICATIONS:
    from notification import models as notification
else:
    notification = None

class BaseUserGroupConfiguration(object):
    order_groups_by = '-created'
    paginate_groups_by = 25

    order_members_by = '-date_joined'
    paginate_members_by = 25

    list_template_name = 'usergroups/group_list.html'
    detail_template_name = 'usergroups/group_detail.html'
    create_group_template_name = 'usergroups/group_form.html'
    edit_group_template_name = 'usergroups/group_form.html'
    create_email_invitation_template_name = \
        'usergroups/create_email_invitation.html'

    confirm_action_template_name = 'usergroups/confirm_action.html'
    done_template_name = 'usergroups/done.html'

    confirmation_messages = {
        'delete': u"Please confirm you want to delete %(group_name)s.",
        'leave_group': (u"Please confirm that you want to leave the group "
                        u"%(group_name)s."),
        'remove_member': (u"Please confirm that you wish to remove "
                          u"%(member_name} from %{group_name)s."),
        'add_admin': (u"Please confirm that %(member_name)s should be made "
                      u"an administrator of %(group_name)s."),
        'revoke_admin': (u"Please confirm that %(member_name)s should be "
                         u"removed from the list of administrators of "
                         u"%(group_name)s."),
        'apply_to_join': u"Do you want to apply to join %(group_name)s?",
        'approve_application': (u"Allow %(applicant_name)s to join "
                                u"%(group_name)s."),
    }

    done_messages = {
        'delete_done': u"Group deleted.",
        'leave_group_done': u"You have left the group %(group_name)s.",
        'remove_member_done': u"Member removed from group.",
        'add_admin_done': u"Admin added to group.",
        'revoke_admin_done': u"Admin removed from group.",
        'group_joined': u"You have joined %(group_name)s",
        'email_invitation_done': u"invitation sent.",
        'application_sent': u"Application sent.",
        'application_failed': u"You are already a member of %(group_name)s.",
        'application_approved': u"Application approved.",
        'application_ignored': u"Application ignored.",
    }

    def __init__(self, slug, model):
        # Make sure that we're extending BaseUserGroup. (This isn't strictly
        # necessary as we're really only interested in the save-logic and the
        # m2m relations, but it's easier than checking and explaining).
        if not issubclass(model, BaseUserGroup):
            raise ValueError(("The model used in usergroups must extend "
                              "BaseUserGroup."))

        self.slug = slug
        self.model = model

    def has_permission(self, user, group):
        return user == group.creator or user in group.admins.all()

    # Forms

    def get_create_group_form(self):
        exclude = ('members', 'admins', 'creator', 'created')
        return modelform_factory(self.model, exclude=exclude)

    def get_edit_group_form(self):
        return self.get_create_group_form()

    def get_email_invitation_form(self):
        return EmailInvitationForm

    # Views

    def group_list(self, request, queryset=None, extra_context=None):
        """Present the visitor with a paginated list of groups.
        
        A custom `QuerySet` can be supplied via the ``queryset`` argument.

        """
        if queryset is None:
            queryset = self.model.objects.all().select_related()
            queryset = queryset.order_by(self.order_groups_by)

        return list_detail.object_list(request, queryset,
                                       template_object_name='group',
                                       extra_context=extra_context or {},
                                       paginate_by=self.paginate_groups_by,
                                       template_name=self.list_template_name)

    def group_detail(self, request, group_id, extra_context=None):
        """Present the user with a detailed view of a group and a paginated
        list of members.
        
        """
        group = get_object_or_404(self.model, pk=group_id)

        queryset = group.members.all().select_related()
        queryset = queryset.order_by(self.order_members_by)

        extra_context = extra_context or {}
        is_admin = group.is_admin(request.user)
        is_owner = request.user == group.creator
        is_member = is_admin or request.user in group.members.all()

        extra_context.update({
            'group': group,
            'is_admin': is_admin,
            'is_owner': is_owner,
            'is_member': is_member,
        })

        return list_detail.object_list(request, queryset,
                                       template_object_name='member',
                                       extra_context=extra_context,
                                       paginate_by=self.paginate_members_by,
                                       template_name=self.detail_template_name)

    @login_required
    def create_group(self, request, extra_context=None):
        """Allow user to create a group. The requesting user will be set as the
        `creator` (and added as an admin in the model-level logic).

        """
        instance = self.model(creator=request.user)

        form_class = self.get_create_group_form()
        form = form_class(request.POST or None, request.FILES or None,
                          instance=instance)

        if form.is_valid():
            instance = form.save()
            url = reverse('usergroups_group_detail',
                          args=(self.slug, instance.pk))
            return http.HttpResponseRedirect(url)

        extra_context = extra_context or {}
        extra_context.update({ 'form': form })

        return direct_to_template(request, extra_context=extra_context,
                                  template=self.create_group_template_name)

    @login_required
    def edit_group(self, request, group_id, extra_context=None):
        """Allow user with administrative privileges to edit a existing
        group.
        
        """
        instance = get_object_or_404(self.model, pk=group_id)

        if not self.has_permission(request.user, instance):
            return http.HttpResponseBadRequest()

        form_class = self.get_edit_group_form()
        form = form_class(request.POST or None, request.FILES or None,
                          instance=instance)

        if form.is_valid():
            instance = form.save()
            url = reverse('usergroups_group_detail',
                          args=(self.slug, instance.pk))
            return http.HttpResponseRedirect(url)

        extra_context = extra_context or None
        extra_context.update({ 'form': form })

        return direct_to_template(request, extra_context=extra_context,
                                  template=self.edit_group_template_name)

    @login_required
    def delete_group(self, request, group_id, extra_context=None):
        """Allow a user with administrative privileges to delete an existing
        group.
        
        """
        group = get_object_or_404(self.model, pk=group_id)

        if not self.has_permission(request.user, group):
            return http.HttpResponseBadRequest()

        if request.method != 'POST':
            return self.confirmation(request, 'delete', group)

        group_id = group.pk
        group.delete()

        url = reverse('usergroups_delete_group_done', args=(self.slug, ))
        return http.HttpResponseRedirect(url)

    # Leave group

    @login_required
    def leave_group(self, request, group_id, extra_context=None):
        """Allow a user to leave a group. Also removes the user from the list
        of admins if applicable.

        Will return a JSON serialized dict if called with headers picked up by
        ``is_ajax()``.

        """
        group = get_object_or_404(self.model, pk=group_id)

        if request.method != 'POST':
            return self.confirmation(request, 'leave_group', group)

        # TODO: We should have a "cannot leave group"-view for this situation.
        if group.admins.count() == 1 and request.user in group.admins.all():
            url = reverse('usergroups_delete_group',
                          args=(self.slug, group.pk))
            return http.HttpResponseRedirect(url)

        group.remove_admin(request.user)
        group.members.remove(request.user)

        extra_context = extra_context or {}

        if request.is_ajax():
            data = { 'user_id': request.user.pk }
            return self.json_done(request, 'leave_group_done', data, group,
                                  extra_context)

        url = reverse('usergroups_leave_group_done',
                      args=(self.slug, group.pk))
        return http.HttpResponseRedirect(url)

    # Manage members

    @login_required
    def remove_member(self, request, group_id, user_id, extra_context=None):
        """Allow a user with administrative privileges to remove a member from
        the group. Also removes the user from the list of admins if applicable.

        Will return a JSON serialized dict if called with headers picked up by
        ``is_ajax()``.

        """
        member = get_object_or_404(User, pk=user_id)
        group = get_object_or_404(self.model, pk=group_id)

        if not self.has_permission(request.user, group):
            return http.HttpResponseBadRequest()

        if member == request.user:
            url = reverse('usergroups_leave_group', args=(self.slug, group.pk))
            return http.HttpResponseRedirect(url)

        extra_context = extra_context or {}
        extra_context.update({
            'member': member,
            'member_name': member.get_full_name() or member.username,
        })

        if request.method != 'POST':
            return self.confirmation(request, 'remove_member', group,
                                     extra_context)

        group.remove_admin(member)
        group.members.remove(member)

        if request.is_ajax():
            data = { 'user_id': member.id }
            return self.json_done(request, 'remove_member_done',
                                  data, group, extra_context)

        url = reverse('usergroups_remove_member_done',
                      args=(self.slug, group.pk, member.pk))
        return http.HttpResponseRedirect(url)

    def remove_member_done(self, request, group_id, user_id,
                           extra_context=None):
        """Notify visitor that member has been removed from the group."""
        group = get_object_or_404(self.model, pk=group_id)
        member = get_object_or_404(User, pk=user_id)

        extra_context = extra_context or {}
        extra_context.update({
            'member': member,
            'member_name': member.get_full_name() or member.username,
        })
        return self.done(request, 'remove_member_done', group, extra_context)

    # Manage admins

    @login_required
    def add_admin(self, request, group_id, user_id, extra_context=None):
        """Allow a user with administrative privileges to make another user
        admin of group.

        """
        group = get_object_or_404(self.model, pk=group_id)
        member = get_object_or_404(User, pk=user_id)

        if not self.has_permission(request.user, group):
            return http.HttpResponseBadRequest()

        extra_context = extra_context or {}
        extra_context.update({
            'member': member,
            'member_name': member.get_full_name() or member.username,
        })

        if request.method != 'POST':
            return self.confirmation(request, 'add_admin', group, 
                                     extra_context)

        group.admins.add(member)
        if member not in group.members.all():
            group.members.add(member)

        if request.is_ajax():
            data = { 'user_id': member.id }
            return self.json_done(request, 'add_admin_done',
                                  data, group, extra_context)

        url = reverse('usergroups_add_admin_done',
                      args=(self.slug, group.pk, member.pk))
        return http.HttpResponseRedirect(url)

    def add_admin_done(self, request, group_id, user_id, extra_context=None):
        group = get_object_or_404(self.model, pk=group_id)
        member = get_object_or_404(User, pk=user_id)

        extra_context = extra_context or None
        extra_context.update({
            'member': member,
            'member_name': member.get_full_name() or member.username,
        })

        return self.done(request, 'add_admin_done', group, extra_context)

    @login_required
    def revoke_admin(self, request, group_id, user_id, extra_context=None):
        """Allow a user with administrative privileges to remove a user from
        the list of admins in group.

        Will return a JSON serialized dict if called with headers picked up by
        ``is_ajax()``.

        """
        group = get_object_or_404(self.model, pk=group_id)
        member = get_object_or_404(User, pk=user_id)

        if not self.has_permission(request.user, group):
            return http.HttpResponseBadRequest()

        extra_context = extra_context or None
        extra_context.update({
            'member': member,
            'member_name': member.get_full_name() or member.username,
        })

        if request.method != 'POST':
            return self.confirmation(request, 'revoke_admin', group, 
                                     extra_context)

        group.remove_admin(member)

        if request.is_ajax():
            data = { 'user_id': member.id }
            return self.json_done(request, 'revoke_admin_done', data, group,
                                  extra_context)

        url = reverse('usergroups_revoke_admin_done',
                      args=(self.slug, group.pk, member.pk))
        return http.HttpResponseRedirect(url)

    def revoke_admin_done(self, request, group_id, user_id,
                          extra_context=None):
        group = get_object_or_404(self.model, pk=group_id)
        member = get_object_or_404(User, pk=user_id)

        extra_context = extra_context or {}
        extra_context.update({
            'member': member,
            'member_name': member.get_full_name() or member.username,
        })

        return self.done(request, 'add_admin_done', group, extra_context)

    # Invitations

    @login_required
    def create_email_invitation(self, request, group_id, extra_context=None):
        """Allow a user with administrative privileges to create and send an
        invitation to join group via e-mail.
        
        """
        group = get_object_or_404(self.model, pk=group_id)

        if not self.has_permission(request.user, group):
            return http.HttpResponseBadRequest()

        form_class = self.get_email_invitation_form()
        form = form_class(user=request.user, group=group,
                          data=request.POST or None)
        if form.is_valid():
            form.send_invitations(self.slug)
            url = reverse('usergroups_email_invitation_done',
                          args=(self.slug, group.pk))
            return http.HttpResponseRedirect(url)

        extra_context = extra_context or {}
        extra_context.update({
            'form': form,
            'group': group,
        })

        template_name = self.create_email_invitation_template_name
        return direct_to_template(request, extra_context=extra_context,
                                  template=template_name)

    @login_required
    def validate_email_invitation(self, request, group_id, key,
                                  extra_context=None):
        """Allow a user to Validate an ``EmailInvitation``."""
        group = get_object_or_404(self.model, pk=group_id)
        try:
            # TODO: Search on group as well.
            invitation = EmailInvitation.objects.get(secret_key=key)
            invitation.delete()
        except EmailInvitation.DoesNotExist:
            return direct_to_template(request,
                                      template='usergroups/invalid_invitation.html')
        except EmailInvitation.MultipleObjectsReturned:
            invitations = EmailInvitation.objects.filter(secret_key=key)
            invitations.delete()

        group.members.add(request.user)

        return http.HttpResponseRedirect(reverse('usergroups_group_joined',
                                                 args=(self.slug, group.pk)))

    # Applications

    @login_required
    def apply_to_join_group(self, request, group_id, extra_context=None):
        """Allow a user to apply to join group.

        Will return a JSON serialized dict if called with headers picked up by
        ``is_ajax()``.

        """
        group = get_object_or_404(self.model, pk=group_id)

        if request.method != 'POST':
            return self.confirmation(request, 'apply_to_join', group, 
                                     extra_context)

        already_member = request.user in group.members.all()

        if not already_member:
            from django.contrib.contenttypes.models import ContentType
            ctype = ContentType.objects.get_for_model(self.model)
            (application, created) = \
                UserGroupApplication.objects.get_or_create(user=request.user,
                                                           content_type=ctype,
                                                           object_id=group.pk)

            if created and notification:
                context = {
                    'application': application,
                    'group': group,
                }
                notification.send(group.admins.all(),
                                  'usergroups_application', context)

        extra_context = extra_context or {}
        extra_context.update({
            'group': group,
            'already_member': already_member,
        })

        action = already_member and 'application_failed' or 'application_sent'

        if request.is_ajax():
            data = { 'already_member': already_member }
            return self.json_done(request, action, data, group, extra_context)

        return http.HttpResponseRedirect(reverse('usergroups_%s' % action,
                                                 args=(self.slug, group.pk)))

    @login_required
    def approve_application(self, request, group_id, application_id,
                            extra_context=None):
        """Allow a user with administrative privileges to approve an
        application to join group.

        Will return a JSON serialized dict if called with headers picked up by
        ``is_ajax()``.

        """
        group = get_object_or_404(self.model, pk=group_id)
        application = get_object_or_404(UserGroupApplication, pk=application_id)
        applicant = application.user

        if not self.has_permission(request.user, group):
            return http.HttpResponseBadRequest()

        extra_context = extra_context or {}
        extra_context.update({
            'applicant': applicant,
            'applicant_name': applicant.get_full_name() or applicant.username,
        })

        if request.method != 'POST':
            return self.confirmation(request, 'approve_application', group, 
                                     extra_context)

        group.members.add(application.user)
        application_id = application.id
        application.delete()

        if notification:
            context = extra_context.copy()
            context.update({
                'group': group,
            })
            notification.send([applicant], 'usergroups_application_approved',
                              context)

        if request.is_ajax():
            data = {
                'application_id': application_id,
                'user_id': applicant.id,
            }
            return self.json_done(request, 'application_approved', data,
                                  extra_context)

        url = reverse('usergroups_application_approved',
                      args=(self.slug, group.pk))
        return http.HttpResponseRedirect(url)

    @login_required
    def ignore_application(self, request, group_id, application_id,
                           extra_context=None):
        """Allow a user with administrative privileges to silently reject an
        application.

        Will return a JSON serialized dict if called with headers picked up by
        ``is_ajax()``.

        """
        group = get_object_or_404(self.model, pk=group_id)
        application = get_object_or_404(UserGroupApplication, pk=application_id)
        applicant = application.user

        if not self.has_permission(request.user, group):
            return http.HttpResponseBadRequest()

        extra_context = extra_context or {}
        extra_context.update({
            'applicant': applicant,
            'applicant_name': applicant.get_full_name() or applicant.username,
        })

        if request.method != 'POST':
            return self.confirmation(request, 'ignore_application', group, 
                                     extra_context)

        application_id = application.pk
        application.delete()

        if request.is_ajax():
            return self.json_done(request, 'application_ignored', data,
                                  group, extra_context)

        url = reverse('usergroups_application_ignored',
                      args=(self.slug, group.pk))
        return http.HttpResponseRedirect(url)

    # Helpers

    def render_helper(self, request, action, group, message, template_name,
                      extra_context=None):
        """Setup a context common for confirmation- and done views,
        interpolate `message` with said context and render `template_name`.

        """
        extra_context = extra_context or {}
        extra_context.update({ 'action': action })
        if group is not None:
            extra_context.update({
                'group': group,
                'group_name': group.name,
            })
        message = message % extra_context
        extra_context.update({ 'message': message })
        return direct_to_template(request, extra_context=extra_context,
                                  template=self.confirm_action_template_name)

    def confirmation(self, request, action, group, extra_context=None):
        """Simple helper-view that should present the visitor with a form
        that can be used to perform a POST-request when such is required
        by the original view.

        The ``action`` argument contains a string used to identify the
        original view (typically to generate sane instructions).

        """
        message = self.confirmation_messages[action]
        template_name = self.confirm_action_template_name
        return self.render_helper(request, action, group, message,
                                  template_name, extra_context)

    def done(self, request, action, group=None, extra_context=None):
        """Simple helper-view that should present the visitor with a message
        letting him/her know that an action has been performed.

        See ``BaseUserGroupConfiguration.confirmation()`` for information on
        arguments.
        
        """
        message = self.done_messages[action]
        return self.render_helper(request, action, group, message,
                                  self.done_template_name, extra_context)

    def json_done(self, request, action, data=None, group=None,
                  extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({
            'group': group,
            'group_name': group.name,
            'action': action,
        })

        data = data or {}
        data.update({
            'message': self.done_messages[action] % extra_context,
        })

        return http.HttpResponse(simplejson.dumps(data, ensure_ascii=False),
                                 mimetype='application/json')


class ConfigurationAlreadyRegistered(Exception):
    pass


class ConfigurationNotRegistered(Exception):
    pass


class GroupOptions(object):
    __shared_state = { 'configurations': {} }

    def __init__(self):
        self.__dict__ = self.__shared_state

    def register(self, key, model, configuration=BaseUserGroupConfiguration):
        try:
            self.configurations[key]
            raise ConfigurationAlreadyRegistered
        except KeyError:
            self.configurations[key] = configuration(slug=key, model=model)

    def get(self, key):
        try:
            return self.configurations[key]
        except KeyError:
            raise ConfigurationNotRegistered


options = GroupOptions()

register = options.register
get = options.get
