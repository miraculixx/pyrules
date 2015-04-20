#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    print os.path.abspath('../..')
    sys.path.append(os.path.abspath('../..'))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "examples.sample.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
