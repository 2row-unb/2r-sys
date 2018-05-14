import logging
from invoke import task

from src import system


def _setup_logging(level):
    """
    Setup logging level
    """
    logging.basicConfig(
        format='%(levelname)s: %(message)s',
        level=getattr(logging, level.upper())
    )

@task
def install(ctx):
    cmd = 'pip install -r requirements.txt'
    result = ctx.run(cmd, hide=True, warn=True)
    print(result.stdout.splitlines()[-1])


@task
def run(ctx, instance=None, log='WARNING'):
    """
    Task to run 2RSystem
    """
    _setup_logging(log)
    system.start(instance)
