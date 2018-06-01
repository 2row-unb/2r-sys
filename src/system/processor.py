"""
Module to filter and process all data
"""
from ..madgwick.madgwickahrs import MadgwickAHRS
import numpy
import logging
import gabby


class Processor(gabby.Gabby):
    """
    Class to process IMU data comming from 2RE-Suit
    """

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.ahrs = MadgwickAHRS()

    def transform(self, message):
        logging.info(f'Transforming data: {message.data}')

        raw_data = message.data

        self.AHRS_update(raw_data)

        matrix = self.AHRS_rotation_matrix()

        accel = raw_data[0:3]
        matrix.extend(accel)

        mag = raw_data[6:9]
        matrix.extend(mag)

        return [gabby.Message(matrix, self.output_topics)]

    def AHRS_update(self, data):
        accel = data[0:3]
        gyro = data[3:6]
        mag = data[6:9]
        self.ahrs.update(mag, accel, gyro)

    def AHRS_quaternion(self):
        return self.ahrs.quaternion

    def AHRS_angle_axis(self):
        return self.ahrs.quaternion.to_angle_axis()

    def AHRS_euler_angles(self):
        return self.ahrs.quaternion.to_euler_angles()

    def AHRS_rotation_matrix(self):
        w, x, y, z = self.ahrs.quaternion

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