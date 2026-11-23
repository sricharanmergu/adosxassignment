import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from django.core.management import execute_from_command_line
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
execute_from_command_line(sys.argv)
