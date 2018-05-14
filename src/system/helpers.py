"""
Module with some helper functions
"""
import logging

def make_runner(cls):
    def runner(obj=None):
        """
        Run an instance of receiver
        """
        if not obj:
            obj = cls()
        logging.info("Running")
        obj.run()
        return obj

    return runner
