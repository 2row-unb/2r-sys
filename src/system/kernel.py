"""
Kernel module is responsible to handle IMUs and Strain Gage
"""
import gabby
import logging


class Kernel(gabby.Gabby):
    def transform(self, message):
        logging.debug(
            f"Received message, data: {message.payload.decode('utf-8')}")
        imu_data = [float(x) for x in
                    message.payload.decode('utf-8').split(';')]

        buttons_info = self.get_buttons()
        weight_info = self.get_weight()
        time_info = self.get_time()

        data = [*imu_data, weight_info, time_info, *buttons_info]
        return [gabby.Message(data, self.output_topics)]

    def get_time(self):
        return 129387134

    def get_buttons(self):
        return [1, 0, 1]

    def get_weight(self):
        return 13255.0
