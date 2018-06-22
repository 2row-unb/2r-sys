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
        self.imus =[[0.00]*9, [0.00]*9]

        super().__init__(*args, **kwargs)

    def transform(self, client, message):
        logging.info(f'Received message from {message.topic}')

        if message.topic == 'ek':
            logging.debug(
                f"Data: {message.payload.decode('utf-8').split(';')}"
            )
            *imu_data, imu_id = [float(x) for x in
                        message.payload.decode('utf-8').split(';')]

            self.imus[int(imu_id)] = imu_data
            controller_data = [
                *self.imus[0], *self.imus[1], self.weight_info, time.time()
            ]
            return [
                gabby.Message(
                    controller_data,
                    self.output_topics.filter_by(name='kernel_controller')
                )
            ]

        elif message.topic == 'kernelcontrol_kernel':
            logging.debug("Received new force measure")
            decoded_msg = gabby.Message.decode(
                message.payload,
                self.input_topics.filter_by(name='kernelcontrol_kernel')
            )
            self.weight_info, = decoded_msg.data

        return []
