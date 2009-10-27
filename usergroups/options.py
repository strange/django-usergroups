from django import http
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms.models import modelform_factory
from django.shortcuts import get_object_or_404
from django.utils import simplejson
from django.views.generic import list_detail
from django.views.generic.simple import direct_to_template
from django.conf import settings

from usergroups.models import BaseUserGroup
from usergroups.decorators import group_admin_required
from usergroups.forms import EmailInvitationForm
from usergroups.models import EmailInvitation
from usergroups.models import UserGroupApplication
from usergroups.models import UserGroupInvitation

# TODO: Deal with extra context
# TODO: Check admin permissions.
# TODO: Template names as class vars.
# TODO: POST instead of GET for views changing the state of app.

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
    delete_group_confirm_template_name = 'usergroups/delete_group_confirm.html'

    def __init__(self, slug, model):
        # Make sure that we're extending BaseUserGroup. (This isn't strictly
        # necessary as we're really only interested in the save-logic and the
        # admins m2m, but it's easier than checking and explaining)
        if not issubclass(model, BaseUserGroup):
            raise ValueError(("The model used in usergroups must extend "
                              "BaseUserGroup."))

        self.slug = slug
        self.model = model

    def has_permission(self, user, group):
        return user in group.admins.all()

    # Forms

    def get_create_group_form(self):
        exclude = ('members', 'admins', 'creator', 'created')
        return modelform_factory(self.model, exclude=exclude)

    def get_edit_group_form(self):
        return self.get_create_group_form()

    # Views

    def group_list(self, request, queryset=None, extra_context=None):
        """A paginated list of groups."""
        if queryset is None:
            queryset = self.model.objects.all().select_related()
            queryset = queryset.order_by(self.order_groups_by)

        return list_detail.object_list(request, queryset,
                                       template_object_name='group',
                                       extra_context=extra_context or {},
                                       paginate_by=self.paginate_groups_by,
                                       template_name=self.list_template_name)

    def group_detail(self, request, group_id, extra_context=None):
        """List of members in a group, information and management."""
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
        """Create a new group. The requesting user will be set as the creator
        (and subsequently an admin in the underlying interface).

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
        """Edit an existing user group.

        """
        instance = get_object_or_404(self.model, pk=group_id)
        form_class = self.get_edit_group_form()

        form = form_class(request.POST or None, request.FILES or None,
                          instance=instance)
        if form.is_valid():
            instance = form.save()
            return http.HttpResponseRedirect(reverse('usergroups_group_detail',
                                                     args=(self.slug, instance.pk)))

        extra_context = extra_context or None
        extra_context.update({ 'form': form })

        return direct_to_template(request, extra_context=extra_context,
                                  template=self.edit_group_template_name)

    @login_required
    def delete_group(self, request, group_id, extra_context=None):
        """Delete an existing group and render a template."""
        group = get_object_or_404(self.model, pk=group_id)

        if request.method == "POST":
            group.delete()
            return http.HttpResponseRedirect(reverse('usergroups_delete_group_done'))

        extra_context = extra_context or {}
        extra_context.update({ 'group': group })

        template_name = self.delete_group_confirm_template_name
        return direct_to_template(request, extra_context=extra_context,
                                  template=template_name)

    # Manage members and admins

    @login_required
    def remove_member(self, request, group_id, user_id, extra_context=None):
        """Remove a member from the group. Also removes the user from the list
        of admins if applicable.

        Will return a JSON serialized dict if called with headers picked up by
        ``is_ajax()``.

        """
        user = get_object_or_404(User, pk=user_id)
        if user == request.user:
            return http.HttpResponseRedirect(reverse('usergroups_leave_group',
                                                args=[group.pk]))
        group = get_object_or_404(self.model, pk=group_id)
        group.remove_admin(user)
        group.members.remove(user)
        if request.is_ajax():
            response = {
                'message': 'Member removed from group',
                'user_id': user.id,
            }
            return http.HttpResponse(simplejson.dumps(json_response),
                                mimetype='application/javascript')

        return http.HttpResponseRedirect(reverse('usergroups_group_detail',
                                                 args=(self.slug, group.pk)))

    @login_required
    def add_admin(self, request, group_id, user_id, extra_context={}):
        """Add a user to the list of users with administrative privilegies in a
        group.

        """
        group = get_object_or_404(self.model, pk=group_id)
        user = get_object_or_404(User, pk=user_id)
        group.admins.add(user)

        # The interface should prevent this from ever being needed.
        if user not in group.members.all():
            group.members.add(user)
        return http.HttpResponseRedirect(reverse('usergroups_group_detail',
                                                 args=(self.slug, group.pk)))

    @login_required
    def revoke_admin(self, request, group_id, user_id, extra_context={}):
        """Revoke an admins's administrative privilegies in a group.

        Will return a JSON serialized dict if called with headers picked up by
        ``is_ajax()``.

        """
        group = get_object_or_404(self.model, pk=group_id)
        user = get_object_or_404(User, pk=user_id)
        group.remove_admin(user)
        if request.is_ajax():
            response = {
                'message': 'Admin rights for user revoked',
                'user_id': user.pk,
            }
            return http.HttpResponse(simplejson.dumps(json_response),
                                mimetype='application/javascript')

        return http.HttpResponseRedirect(reverse('usergroups_group_detail',
                                                 args=(self.slug, group.pk)))

    @login_required
    def leave_group(self, request, group_id, extra_context=None):
        """Allow a user to leave a group. Also removes the user from the list
        of admins if applicable.

        Will return a JSON serialized dict if called with headers picked up by
        ``is_ajax()``.

        """
        group = get_object_or_404(self.model, pk=group_id)

        if group.admins.count() <= 1 and request.user in group.admins.all():
            return HttpResponseRedirect(reverse('usergroups_delete_group',
                                                args=(self.slug, group.pk)))

        group.remove_admin(request.user)
        group.members.remove(request.user)

        if request.is_ajax():
            response = {
                'message': 'You have left the group',
                'user_id': request.user.id,
            }
            return http.HttpResponse(simplejson.dumps(json_response),
                                     mimetype='application/javascript')

        return http.HttpResponseRedirect(reverse('usergroups_group_detail',
                                                 args=(self.slug, group.pk)))

    # Invitations and applications

    @login_required
    def create_email_invitation(self, request, group_id, extra_context=None):
        """Create and send an invitation to a ``UserGroup`` via e-mail."""
        group = get_object_or_404(self.model, pk=group_id)
        if request.method == 'POST':
            form = EmailInvitationForm(user=request.user, group=group,
                                       data=request.POST)
            if form.is_valid():
                form.send_invitations(self.slug)
                url = reverse('usergroups_group_detail',
                              args=(self.slug, group.pk))
                return http.HttpResponseRedirect(url)
        else:
            form = EmailInvitationForm(user=request.user, group=group)

        return direct_to_template(request, extra_context=locals(),
                                         template='usergroups/create_email_invitation.html')

    @login_required
    def validate_email_invitation(self, request, group_id, key,
                                  extra_context=None):
        """Validate an invitation."""
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


    def group_joined(self, request, group_id, extra_context=None):
        group = get_object_or_404(self.model, pk=group_id)
        return direct_to_template(request, extra_context=locals(),
                                         template='usergroups/group_joined.html')

    @login_required
    def approve_application(self, request, group_id, application_id,
                            extra_context=None):
        """Approve an application.

        Will return a JSON serialized dict if called with headers picked up by
        ``is_ajax()``.

        """
        group = get_object_or_404(self.model, pk=group_id)
        application = get_object_or_404(UserGroupApplication, pk=application_id)
        group.members.add(application.user)
        application_id = application.id

        applicant = application.user
        context = {
            'group': group,
            'applicant': applicant,
        }

        application.delete()

        if notification:
            notification.send([applicant], 'usergroups_application_approved',
                              context)

        if request.is_ajax():
            response = {
                'message': 'Application approved',
                'user_id': application.user.id,
                'application_id': application_id,
            }
            return http.HttpResponse(simplejson.dumps(json_response),
                                mimetype='application/javascript')


        return http.HttpResponseRedirect(reverse('usergroups_group_detail',
                                                args=(self.slug, group.pk)))

    @login_required
    def ignore_application(self, request, group_id, application_id,
                           extra_context=None):
        """Reject an application.

        Will return a JSON serialized dict if called with headers picked up by
        ``is_ajax()``.

        """
        group = get_object_or_404(self.model, pk=group_id)
        application = get_object_or_404(UserGroupApplication, pk=application_id)
        application_id = application.pk
        application.delete()

        if request.is_ajax():
            response = {
                'message': 'Application ignored.',
                'user_id': application.user.id,
                'application_id': application_id,
            }
            return http.HttpResponse(simplejson.dumps(json_response),
                                mimetype='application/javascript')


        return http.HttpResponseRedirect(reverse('usergroups_group_detail',
                                                 args=(self.slug, group.pk)))

    @login_required
    def apply_to_join_group(self, request, group_id, extra_context=None):
        """Allow a user to apply to join a user group.

        Will return a JSON serialized dict if called with headers picked up by
        ``is_ajax()``.

        """
        group = get_object_or_404(self.model, pk=group_id)
        already_member = request.user in group.members.all()
        if not already_member:
            try:
                from django.contrib.contenttypes.models import ContentType
                ctype = ContentType.objects.get_for_model(group)
                application = UserGroupApplication.objects.get(user=request.user,
                                                               content_type=ctype,
                                                               object_id=group.pk)
                application.created = datetime.datetime.now()
                application.save()
            except UserGroupApplication.DoesNotExist:
                application = UserGroupApplication.objects.create(user=request.user,
                                                                  group=group)
                context = {
                    'application': application,
                    'group': group,
                }
                if notification:
                    notification.send(group.admins.all(), 'usergroups_application', context)

        extra_context = { 'group': group, 'already_member': already_member }

        if request.is_ajax():
            response = {
                'message': already_member and 'You\'re already a member of group' or 'Application sent',
                'already_member': already_member,
            }
            return HttpResponse(simplejson.dumps(json_response),
                                mimetype='application/javascript')

        return direct_to_template(request, extra_context=extra_context,
                                         template='usergroups/application.html')


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
