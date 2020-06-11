import os
from setuptools import setup, find_packages


path = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(path, 'README.md')).read()


setup(
    name='django_module_users',
    version='0.3',
    packages=find_packages(),
    description='Django Module Users',
    long_description=README,
    author='eduardo',
    author_email='edunola13@gmail.com',
    package_data={
        '': ['*.txt', '*.html']
    },
    include_package_data=True,
    url='https://github.com/edunola13/libs-python-django-module-users',
    license='MIT',
    install_requires=[
        'Django >= 3.0',
        'django-filter >= 2.2.0',
        'djangorestframework >= 3.10.3',
        'django-simple-email-confirmation >= 0.60',
        'django-rest-passwordreset >= 1.1.0',
        'celery >= 4.1.1'
    ],
)
