from __future__ import absolute_import, unicode_literals

from celery import shared_task

from django.core import management


@shared_task(name="create_fixture_install")
def import_fixture():
    """Execute custom django-admin command to create and install fixture in Unlocode table"""
    management.call_command(
        'create_install_fixture',
        'unlocode/fixtures',
        'http://www.unece.org/fileadmin/DAM/cefact/locode/loc192csv.zip',
        verbosity=0)
