=====
Module Users
=====

Module Users is a Django app for basic functionallity of Users.

Quick start
-----------

1. Add "django_module_users" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'simple_email_confirmation',
    	'django_rest_passwordreset',
    	'django_module_users',
    ]

2. Include the module users URLconf in your project urls.py like this::

    path('u/', include('django_module_users.urls')),

Or add the custom rule like you wish.

3. Add the next settings:
	- AUTH_USER_MODEL = 'django_module_users.User'
	- SIMPLE_EMAIL_CONFIRMATION_KEY_LENGTH: Length code.
	- DEFAULT_FROM_EMAIL: Email from send emails.
    - FRONT_URL: URL used in emails to go back to web site.
	- CELERY_*: Celery options.
    - DJ_MOD_USERS: Module users specific settings:
        - PERMISSIONS: Permissions for admin api.

4. Run ``python manage.py migrate`` to create the users models.

5. Override model User o templates:
    - emails/users/rest_password.html and .txt
    - emails/users/verification.html and .txt


=====
Developers Module
=====

You need develop your module like any django app. After that you need a test_settings because there is no django_project y run makemigrations y tests with this settings. Fot that we use the edited manage.py

Steps after development:
 - python manage.py makemigrations
 - python manage.py test
