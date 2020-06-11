# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import binascii
import secrets

from django.utils.translation import gettext as _

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.dispatch import receiver

from simple_email_confirmation.models import SimpleEmailConfirmationUserMixin, EmailAddress
from django_rest_passwordreset.signals import reset_password_token_created

from .tasks import send_email


USER_TYPE_PERSON = "PERSON"
USER_TYPE_APP = "APP"

USER_TYPE_CHOICES = (
    (USER_TYPE_PERSON, 'Person'),
    (USER_TYPE_APP, 'App')
)


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    reset_password_token.user.send_email_reset_password(reset_password_token.key)


class User(SimpleEmailConfirmationUserMixin, AbstractUser):
    type = models.CharField(max_length=32,
                            default=USER_TYPE_PERSON,
                            choices=USER_TYPE_CHOICES)

    @classmethod
    def create(cls, username, email, password,
               email_validated=False, **extra_fields):
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **extra_fields
        )

        if email_validated is True:
            user.validate_email()
        else:
            user.send_email_verification()

        return user

    def validate_email(self):
        """Manual validate email."""
        self.confirm_email(self.confirmation_key)
        return self.is_confirmed

    def change_email(self, new_email):
        self.email = new_email
        self.username = new_email  # Esto es mientras lo mantengan como lo mismo
        self.save()

        email_address = EmailAddress.objects.get(user=self)
        email_address.email = new_email
        email_address.save()
        email_address.reset_confirmation()

        self.send_email_verification()

    def send_email_reset_password(self, key):
        send_email(
            self.email,
            _('Reset Password'),
            'emails/users/reset_password',
            {
                'reset_password_url': '{}/reset/{}/'.format(
                    settings.FRONT_URL,
                    key
                )
            }
        )

    def send_email_verification(self):
        send_email(
            self.email,
            _('Verification Email'),
            'emails/users/verification',
            {
                'link_confirmation': '{}/confirm/{}/{}'.format(
                    settings.FRONT_URL,
                    self.id,
                    self.confirmation_key
                )
            }
        )


class Permission(models.Model):
    name = models.CharField(max_length=128)
    content_type = models.ForeignKey(
        ContentType,
        related_name="+",
        on_delete=models.CASCADE,
        null=True)
    object_id = models.CharField(max_length=50, null=True)
    object_related = GenericForeignKey('content_type', 'object_id')


class Role(models.Model):
    name = models.CharField(max_length=64, unique=True)
    users = models.ManyToManyField(User)
    permissions = models.ManyToManyField(Permission)


class ApiKey(models.Model):
    key = models.CharField(max_length=64, unique=True)
    user = models.ForeignKey(User,
                             null=False,
                             related_name="keys",
                             on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ApiKey, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(secrets.token_bytes()).decode()
