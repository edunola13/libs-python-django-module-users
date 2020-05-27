# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.routers import DefaultRouter
from django.conf.urls import url, include

from .api import (
    UserViewSet, ApiKeyViewSet,
    RoleViewSet, PermissionViewSet,
)
from .me_api import (
    UserMeView, UserRegisterView,
    ConfirmEmailView, ResendEmailView,
    ChangeEmailView, ChangePasswordView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'keys', ApiKeyViewSet, basename='keys')
router.register(r'permissions', PermissionViewSet, basename="permissions")
router.register(r'roles', RoleViewSet, basename="roles")

urlpatterns = [
    url(r'^me/$', UserMeView.as_view(), name='user_me'),
    url(r'^me/change_email/$', ChangeEmailView.as_view(), name='change_email'),
    url(r'^me/change_password/$', ChangePasswordView.as_view(), name='change_password'),
    url(r'^register/$', UserRegisterView.as_view(), name='register'),
    url(r'^confirm_email/$', ConfirmEmailView.as_view(), name='confirm_email'),
    url(r'^resend_email/$', ResendEmailView.as_view(), name='resend_email'),
    url(r'^password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
]

urlpatterns += router.urls
