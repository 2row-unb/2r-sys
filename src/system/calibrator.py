import time

DESIRED_SAMPLES = 1000
ACCEPTED_DIFFERENCE = 10.0
TIME_TO_START = 10

class Calibrator():
    def __init__(self):
        self._start_time = time.time()
        self._axes_sums = [None, None, None]
        self._samples = 0

    def add_sample(self, sample_data, current_time):
        time_elapsed = current_time - self._start_time
        if time_elapsed < TIME_TO_START or self.ready():
            return

        if self._axes_sums[0] == None:
            self._axes_sums = sample_data
            self._samples = 1
        else:
            accepted_sample = True
            for i in range(0, len(self._axes_sums)):
                average = self._axes_sums[i] / self._samples
                difference = abs(average - sample_data[i])
                if difference > ACCEPTED_DIFFERENCE:
                    accepted_sample = False
                    break

            if accepted_sample is True:
                for i in range(0, len(self._axes_sums)):
                    self._axes_sums[i] += sample_data[i]
                self._samples += 1
            else:
                self._axes_sums = sample_data
                self._samples = 1

    def ready(self):
        return self._samples >= DESIRED_SAMPLES

    def averages(self):
        results = []
        for i in range(0, len(self._axes_sums)):
            results.append(self._axes_sums[i] / self._samples)
        return results
