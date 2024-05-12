import asyncio
import django
import sys
import os

def setup_database():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.database.settings')

def initialize_database():
    setup_database()

    django.setup()

    run_db_cli([
        __name__,
        "makemigrations",
    ])

    run_db_cli([
        __name__,
        "migrate"
    ])

def main():
    initialize_database()

    try:
        import uvloop
    except ImportError:
        pass
    else:
        uvloop.install()

    from .bot.op import start_bot
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())

def run_db_cli(args=sys.argv):
    setup_database()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(args)