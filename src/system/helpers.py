"""
Module with some helper functions
"""
import logging

def make_runner(cls):
    def runner(obj=None):
        """
        Run an instance of a class
        """
        if not obj:
            obj = cls()
        logging.info(f'Running an instance of {cls.__name__}')
        obj.run()
        return obj

    return runner
