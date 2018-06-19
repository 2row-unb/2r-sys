"""
Module to filter and process all data
"""
from ..madgwick.madgwickahrs import MadgwickAHRS
import logging
import gabby

IMUS = 1

class Processor(gabby.Gabby):
    """
    Class to process IMU data comming from 2RE-Suit
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ahrs = []

        for i in range(0, IMUS):
            self.ahrs.append(MadgwickAHRS())

    def transform(self, message):
        logging.info(f'Transforming data: {message.data}')

        for i in range(0, IMUS):
            raw_data = message.data[i * 9:(i + 1) * 9]
            self.AHRS_update(self.ahrs[i], raw_data)

        v_data = self.euler_angles_visualizer_data(message.data)

        return [gabby.Message(v_data, self.output_topics)]

    def visualizer_data(self, input_data):
        data = []

        for i in range(0, IMUS):
            data.extend(self.AHRS_rotation_matrix(self.ahrs[i]))
            raw_data = input_data[i * 9:(i + 1) * 9]
            accel = raw_data[0:3]
            data.extend(accel)
            mag = raw_data[6:9]
            data.extend(mag)

        weight, timestamp = input_data[9 * 2:] # TODO: change the value 2 to IMUS when ready
        data.extend([weight, timestamp])

        return data

    def euler_angles_visualizer_data(self, input_data):
        data = []

        for i in range(0, IMUS):
            roll, pitch, yaw = self.ahrs[i].quaternion.to_euler_angles()
            data.extend([roll, pitch, yaw])
            w, x, y, z = self.ahrs[i].quaternion.get_q()
            data.extend([x, y, z, w])

        weight, timestamp = input_data[9 * 2:] # TODO: change the value 2 to IMUS when ready
        data.extend([weight, timestamp])

        return data

    def AHRS_update(self, ahrs, data):
        accel = data[0:3]
        gyro = data[3:6]
        mag = data[6:9]
        ahrs.update(mag, accel, gyro)

    def AHRS_rotation_matrix(self, ahrs):
        w, x, y, z = ahrs.quaternion

        tx = 2 * x
        ty = 2 * y
        tz = 2 * z
        twx = tx * w
        twy = ty * w
        twz = tz * w
        txx = tx * x
        txy = ty * x
        txz = tz * x
        tyy = ty * y
        tyz = tz * y
        tzz = tz * z

        matrix = []
        matrix.append(1.0 - (tyy + tzz))
        matrix.append(txy - twz)
        matrix.append(txz + twy)
        matrix.append(txy + twz)
        matrix.append(1.0 - (txx + tzz))
        matrix.append(tyz - twx)
        matrix.append(txz - twy)
        matrix.append(tyz + twx)
        matrix.append(1.0 - (txx + tyy))

        return matrix
