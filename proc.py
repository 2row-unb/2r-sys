from multiprocessing import Process
import time

if __name__ == "__main__":
    p = Process(target=lambda x: time.sleep(x), args=(10,))
    print("Start")
    p.start()
    p.join()
    print("Stop")
