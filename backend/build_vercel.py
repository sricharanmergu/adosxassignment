"""Seed the read-only SQLite database before Vercel builds the Django function."""
import os

import django
from django.core.management import call_command


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

call_command("migrate", interactive=False)
call_command("import_data")
call_command("collectstatic", interactive=False, clear=True)
