"""
Module to filter and process all data
"""
import logging
import gabby

from ..madgwick.madgwickahrs import MadgwickAHRS
from .calibrator import Calibrator
from .state import State
from .config.settings import N_IMUS


class Processor(gabby.Gabby):
    """
    Class to process IMU data comming from 2RE-Suit
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ahrs = [MadgwickAHRS()] * N_IMUS
        self._calibrators = [Calibrator()] * N_IMUS
        self._averages = []
        self._state = State.INITIAL
        self._enable_change = True

    def transform(self, message):
        logging.info(f'Transforming data: {message.data}')
        logging.info('Processor state: ' + 'INITIAL' if self._state == State.INITIAL else 'RUNNING')

        for i in range(N_IMUS):
            raw_data = message.data[i * 9:(i + 1) * 9]
            self.AHRS_update(self._ahrs[i], raw_data)

        state, current_time = message.data[-2:]

        if state == State.INITIAL and self._enable_change is True:
            self.run_calibration_step(current_time)
        elif state == State.RUNNING:
            self._enable_change = True

        v_data = self.euler_angles_visualizer_data(message.data)

        return [gabby.Message(v_data, self.output_topics)]

    def visualizer_data(self, input_data):
        data = []

        for i in range(N_IMUS):
            data.extend(self.AHRS_rotation_matrix(self._ahrs[i]))
            raw_data = input_data[i * 9:(i + 1) * 9]
            accel = raw_data[0:3]
            data.extend(accel)
            mag = raw_data[6:9]
            data.extend(mag)

        weight, state, timestamp = input_data[9 * 2:] # TODO: change the value 2 to N_IMUS when ready
        data.extend([weight, self._state, timestamp])

        return data

    def euler_angles_visualizer_data(self, input_data):
        data = []

        for i in range(N_IMUS):
            roll, pitch, yaw = self._ahrs[i].quaternion.to_euler_angles()
            data.extend([roll, pitch, yaw])
            w, x, y, z = self._ahrs[i].quaternion.get_q()
            data.extend([x, y, z, w])

        weight, state, timestamp = input_data[9 * 2:] # TODO: change the value 2 to N_IMUS when ready
        data.extend([weight, self._state, timestamp])

        return data

    def run_calibration_step(self, current_time):
        logging.info('Running calibration step')

        if self._state == State.RUNNING:
            self._averages = []
            for i in range(N_IMUS):
                self._calibrators[i].clear()

        self._state = State.INITIAL

        calibrated = all([cal.add_sample(ahrs.quaternion.to_euler_angles(), current_time)
                         for ahrs, cal in zip(self._ahrs, self._calibrators)]
                        )

        if calibrated is True:
            self._state = State.RUNNING
            self._enable_change = False
            for i in range(N_IMUS):
                self._averages.append(self._calibrators[i].averages())


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
