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

        v_data = self.visualizer_data(message.data)

        return [gabby.Message(v_data, self.output_topics)]

    def visualizer_data(self, input_data):
        data = []

        for i in range(0, IMUS):
            raw_data = input_data[i * 9:(i + 1) * 9]
            self.AHRS_update(self.ahrs[i], raw_data)
            data.extend(self.AHRS_rotation_matrix(self.ahrs[i]))
            accel = raw_data[0:3]
            data.extend(accel)
            mag = raw_data[6:9]
            data.extend(mag)

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
