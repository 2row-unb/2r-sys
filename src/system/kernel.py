"""
Kernel module is responsible to handle IMUs and Strain Gage
"""
import gabby
import logging
import time


class Kernel(gabby.Gabby):
    def __init__(self, *args, **kwargs):
        self.weight_info = 0
        self.force_measure = 0.0
        super().__init__(*args, **kwargs)

    def transform(self, client, message):
        logging.info(f'Received message from {message.topic}')

        if message.topic == 'ek':
            logging.debug(
                f"Data: {message.payload.decode('utf-8').split(';')}"
            )
            imu_data = [float(x) for x in
                        message.payload.decode('utf-8').split(';')]

            controller_data = [*imu_data, self.weight_info, time.time()]
            return [
                gabby.Message(
                    controller_data,
                    self.output_topics.filter_by(name='kernel_controller')
                )
            ]
        elif message.topic == 'kernelcontrol_kernel':
            self.weight_info, = message.data

        return []
