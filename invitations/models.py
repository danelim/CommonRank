import datetime

from django.conf import settings
from django.contrib.sites.models import Site
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import signals
from .adapters import get_invitations_adapter, BaseInvitationsAdapter
from .app_settings import app_settings
from .base_invitation import AbstractBaseInvitation


@python_2_unicode_compatible
class Invitation(AbstractBaseInvitation):
    email = models.EmailField(unique=True, verbose_name=_('e-mail address'),
                              max_length=app_settings.EMAIL_MAX_LENGTH)
    created = models.DateTimeField(verbose_name=_('created'),
                                   default=timezone.now)

    @classmethod
    def create(cls, email, inviter=None, **kwargs):
        key = get_random_string(64).lower()
        instance = cls._default_manager.create(
            email=email,
            key=key,
            inviter=inviter,
            **kwargs)
        return instance

    def key_expired(self):
        expiration_date = (
            self.sent + datetime.timedelta(
                days=app_settings.INVITATION_EXPIRY))
        return expiration_date <= timezone.now()

    def send_invitation(self, request, **kwargs):
        print("where fore art thou branko")
        #current_site = kwargs.pop('site', Site.objects.get_current())
        print("goob")
        invite_url = reverse('invitations:accept-invite',
                             args=[self.key])
        print("goob")
        invite_url = request.build_absolute_uri(invite_url, )
        print("goob")
        ctx = kwargs
        ctx.update({
            'invite_url': invite_url,
            #'site_name': current_site.name,
            'email': self.email,
        })
        email_template = 'invitations/email/email_invite'
        print(ctx)
        get_invitations_adapter().send_mail(
            email_template,
            self.email,
            ctx)
        print("goob")
        self.sent = timezone.now()
        self.save()
        print("goob")
        signals.invite_url_sent.send(
            sender=self.__class__,
            instance=self,
            invite_url_sent=invite_url,
            inviter=self.inviter)

    def __str__(self):
        return "Invite: {0}".format(self.email)


# here for backwards compatibility, historic allauth adapter
if hasattr(settings, 'ACCOUNT_ADAPTER'):
    if settings.ACCOUNT_ADAPTER == 'invitations.models.InvitationsAdapter':
        from allauth.account.adapter import DefaultAccountAdapter
        from allauth.account.signals import user_signed_up

        class InvitationsAdapter(DefaultAccountAdapter):

            def is_open_for_signup(self, request):
                if hasattr(request, 'session') and request.session.get(
                        'account_verified_email'):
                    return True
                elif app_settings.INVITATION_ONLY is True:
                    # Site is ONLY open for invites
                    return False
                else:
                    # Site is open to signup
                    return True

            def get_user_signed_up_signal(self):
                return user_signed_up
