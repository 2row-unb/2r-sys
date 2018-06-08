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
def flask(ctx, port='0.0.0.0'):
    import os
    os.environ['FLASK_APP'] = 'src/api/api.py'
    ctx.run(f'flask run -h {port}')


@task
def faker(ctx, mqtt=False, timer=0.3, shot=False):
    import time
    from src.faker.fake_data import data_generator

    if mqtt:
        from paho.mqtt.client import Client
        c = Client()
        c.connect('localhost', 1883, 60)
        gen = data_generator(
            lambda x: c.publish(
                'esp_kernel',
                ";".join(map(lambda a: str(float(a)), x))
            ))
    else:
        gen = data_generator(lambda x: list(map(int, x)))

    while True:
        next(gen)
        time.sleep(timer)
        if shot:
            break
