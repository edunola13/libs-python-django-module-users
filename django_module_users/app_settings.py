# -*- coding: utf-8 -*-

from django.conf import settings

from rest_framework.permissions import IsAdminUser

MOD_USERS = getattr(settings, 'DJ_MOD_USERS', {})

PERMISSIONS = (MOD_USERS.get('PERMISSIONS', None) or [IsAdminUser])
