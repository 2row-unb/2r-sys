"""
Kernel module is responsible to handle IMUs and Strain Gage
"""
import gabby


class Kernel(gabby.Gabby):
    def transform(self, message):
        imu_data = [float(x) for x in
                    message.payload.decode('utf-8').split(';')]

        buttons_info = self.get_buttons()
        weight_info = self.get_weight()

        data = [*imu_data, *buttons_info, weight_info]
        return [gabby.Message(data, self.output_topics)]

    def get_buttons(self):
        return [1.0, 0.0, 1.0]

    def get_weight(self):
        return 13255.0
