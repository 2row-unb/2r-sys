"""
Module to filter and process all data
"""
import logging
import gabby
import time

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
        self._ahrs = [MadgwickAHRS(), MadgwickAHRS()]
        self._calibrators = [Calibrator(), Calibrator()]
        self._averages = [[0.0]*3]*N_IMUS
        self._state = State.INITIAL
        self._can_state_change = True

    def transform(self, client, message):
        logging.info(f'Transforming data: {message.data}')
        logging.info(f'Processor state: {State.name(self._state)}')

        self.update_ahrs(message.data)
        self.calibrate_measures(*message.data[-2:])
        v_data = self.euler_angles_visualizer_data(message.data)

        return [gabby.Message(v_data, self.output_topics)]

    def update_ahrs(self, data):
        for i in range(N_IMUS):
            raw_data = data[i * 9:(i + 1) * 9]
            ax, ay, az, gx, gy, gz, mx, my, mz = raw_data
            logging.info(f'i: {i}')
            self.AHRS_update(self._ahrs[i], [ax, ay, az, gx, gy, gz, mx, my, mz])

    def calibrate_measures(self, controller_state, current_time):
        if controller_state == State.INITIAL and self._can_state_change:
            self.run_calibration_step(current_time)
        elif controller_state == State.RUNNING:
            self._can_state_change = True

    def visualizer_data(self, input_data):
        data = []

        for i in range(N_IMUS):
            data.extend(self.AHRS_rotation_matrix(self._ahrs[i]))
            raw_data = input_data[i * 9:(i + 1) * 9]
            accel = raw_data[0:3]
            data.extend(accel)
            mag = raw_data[6:9]
            data.extend(mag)
        # [TODO] set number of IMUS dinamically
        weight, state, timestamp = input_data[9 * 2:]
        data.extend([weight, self._state, timestamp])

        return data

    def euler_angles_visualizer_data(self, input_data):
        data = []

        for i in range(N_IMUS):
            roll, pitch, yaw = self._ahrs[i].quaternion.to_euler_angles()
            logging.info(f'RAW ROLL: {roll} | AVG: {self._averages[i][0]} | ROLL: {roll - self._averages[i][0]}')
            logging.info(f'RAW PITCH: {pitch} | AVG: {self._averages[i][1]} | PITCH: {pitch - self._averages[i][1]}')
            logging.info(f'RAW YAW: {yaw} | AVG: {self._averages[i][2]} | YAW: {yaw - self._averages[i][2]}')
            roll -= self._averages[i][0]
            pitch -= self._averages[i][1]
            yaw -= self._averages[i][2]
            data.extend([roll, pitch, yaw])
        # [TODO] set number of IMUS dinamically
        weight, state, timestamp = input_data[9 * 2:]
        data.extend([weight, self._state, timestamp])

        return data

    def run_calibration_step(self, current_time):
        logging.info('Running calibration step')

        if self._state == State.RUNNING:
            for cal in self._calibrators:
                cal.clear()
            for ahrs in self._ahrs:
                ahrs.update_gain_timeoff(time.time())
            self._state = State.INITIAL

        calibrated = all(
            [cal.add_sample(ahrs.quaternion.to_euler_angles(), current_time)
             for ahrs, cal in zip(self._ahrs, self._calibrators)]
        )

        if calibrated:
            self._state = State.RUNNING
            self._can_state_change = False
            self._averages = [cal.averages() for cal in self._calibrators]

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

        matrix = [
            1.0 - (tyy + tzz),
            txy - twz,
            txz + twy,
            txy + twz,
            1.0 - (txx + tzz),
            tyz - twx,
            txz - twy,
            tyz + twx,
            1.0 - (txx + tyy),
        ]

        return matrix
