# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template

from celery.decorators import task


@task()
def send_email(to, subject, template, data):
    """ Send email """
    try:
        data['settings'] = settings
        html = get_template('{}.html'.format(template))
        text = get_template('{}.txt'.format(template))
        send_mail(
            subject,
            text.render(data),
            settings.DEFAULT_FROM_EMAIL,
            [to],
            html_message=html.render(data)
        )
    except Exception as e:
        logging.error('SEND_MAIL, to: {0}, template: {1}, error: {2}'.format(to, template, e), exc_info=True)
