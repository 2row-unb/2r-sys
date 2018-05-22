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


@task
def faker(ctx, mqtt=False, timer=0.3, shot=False):
    import time
    from src.faker.fake_data import data_generator

    if mqtt:
        from paho.mqtt.client import Client
        c = Client()
        c.connect('localhost', 1883, 60)
        func = lambda x: c.publish(
            '2rs/receiver/input',
            ";".join(map(lambda a: str(int(a)), x))
        )
    else:
        func = lambda x: list(map(int, x))

    gen = data_generator(func)
    while True:
        next(gen)
        time.sleep(timer)
        if shot:
            break
