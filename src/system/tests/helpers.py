from threading import Thread


class ThRx(Thread):
    def __init__(self, rx):
        Thread.__init__(self)
        self.rx = rx

    def stop(self):
        self.rx.running = False

    def run(self):
        self.rx.run()


def start_receiver(rx):
    rx_th = ThRx(rx)
    rx_th.start()
    return rx_th


def stop_receiver(th):
    th.stop()
    th.join()
