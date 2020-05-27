# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import factory

from django.conf import settings

from rest_framework.test import APITestCase, APIClient

from django.contrib.auth import get_user_model


User = get_user_model()


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = "api@rfid.com"
    email = factory.LazyAttribute(lambda x: x.username)
    password = '123456'
    first_name = "Api"
    last_name = "RFID"
    is_staff = False
    is_active = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", None)
        obj = super(UserFactory, cls)._create(model_class, *args, **kwargs)
        # ensure the raw password gets set after the initial save
        obj.set_password(password)
        obj.save()
        obj.confirm_email(obj.confirmation_key)
        return obj


class APIClient(APIClient):
    pass


class APITestCase(APITestCase):
    client_class = APIClient
    user_factory = UserFactory
