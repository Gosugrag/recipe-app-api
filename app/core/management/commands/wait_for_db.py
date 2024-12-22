"""
Django command to pause execution until database is available
"""
import time

from psycopg2 import OperationalError as Psycopg2OpError
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    def handle(self, *args, **options):
        """Entry point for command"""
        self.stdout.write('Waiting for database...')
        dp_up = False
        while not dp_up:
            try:
                self.check(databases=['default'])
                dp_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write(
                    self.style.ERROR('Database unavailable, '
                                     'waiting 1 second...')
                )
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))
