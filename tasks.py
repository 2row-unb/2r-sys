import logging
from invoke import task


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
def run(ctx, instance=None, rpi_mock=False, log='WARNING'):
    """
    Task to run 2RSystem
    """
    _setup_logging(log)

    if rpi_mock:
        import os
        os.environ['RPI_MOCK'] = 'true'

    from src import system
    system.start(instance)


@task
def faker(ctx, mqtt=False, mqttsn=False, timer=0.3, shot=False):
    import time
    from src.faker.fake_data import data_generator

    if mqtt:
        from paho.mqtt.client import Client
        c = Client()
        c.connect('localhost', 1883, 60)
        gen = data_generator(
            lambda x: c.publish(
                'ek', ";".join(map(lambda a: str(float(a)), x))
            ))
    elif mqttsn:
        from mqttsn.client import Client
        c = Client(host='localhost', port=1885)
        c.connect()
        gen = data_generator(
            lambda x: c.publish(
                'ek', ";".join(map(lambda a: str(float(a)), x))
            ))

    while True:
        next(gen)
        time.sleep(timer)
        if shot:
            break
