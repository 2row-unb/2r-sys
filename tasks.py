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
def run(ctx, log='WARNING'):
    """
    Task to run 2RSystem
    """
    _setup_logging(log)
    logging.info(f'Running 2RSystem')
