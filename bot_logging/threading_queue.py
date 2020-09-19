"""Based on Consumer producer pattern"""
import threading
from threading import Thread, Condition
from wrapt import synchronized

import time
import random



queue = []
condition = Condition()


def send_message(msg):
    global queue
    condition.acquire()
    queue.append(msg)
    condition.notify()
    condition.release()


class ProducerThread(Thread):
    def __init__(self, name, **kwargs):
        super(ProducerThread, self).__init__(**kwargs)
        self.name = name

    def run(self):
        l = range(70)
        for i in l:
            time.sleep(random.random() * 0.1)
            send_message(f"{self.name} {i}")


lock = threading.Lock()
class Singleton(type):
    # get from https://stackoverflow.com/questions/50566934
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._locked_call(*args, **kwargs)
        return cls._instances[cls]

    @synchronized(lock)
    def _locked_call(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]



class ConsumerThread(Thread, metaclass=Singleton):
    def __init__(
        self, sendDBfn, max_batch=30, min_batch=10, max_history_len=200, max_time2update=5.0, **kwargs
    ):
        super(ConsumerThread, self).__init__(**kwargs)
        self.sendDB = sendDBfn
        self.MAX_BATCH = max_batch
        self.MIN_BATCH = min_batch
        self.MAX_HISTORY_LEN = max_history_len
        self.MAX_TIME2UPDATE = max_time2update
        self._producer_number = 1
        self._first_producer = True
        self.mutex_producer_number = threading.Lock()
        self.start()

    def __check_last_producer(self):
        self.mutex_producer_number.acquire()
        is_last = self._producer_number <= 0
        self.mutex_producer_number.release()
        return is_last

    def add_producer(self):
        self.mutex_producer_number.acquire()
        if self._first_producer:
            self._first_producer = False
        else:
            self._producer_number += 1
        self.mutex_producer_number.release()

    def del_producer(self):
        self.mutex_producer_number.acquire()
        self._producer_number -= 1
        self.mutex_producer_number.release()

    def run(self):
        global queue
        previous_iter_empty_queue = True
        last_time_one_added = -1
        i = 0
        while True:
            condition.acquire()
            if not queue:
                print("Nothing in queue, consumer is waiting")
                if self.__check_last_producer():
                    break
                condition.wait()
                print("Producer added something to queue and notified the consumer")

            r = None
            if len(queue) == 0:
                previous_iter_empty_queue = True
            elif previous_iter_empty_queue:
                previous_iter_empty_queue=False
                last_time_one_added = time.time()

            time2update = time.time() - last_time_one_added > self.MAX_TIME2UPDATE
            if len(queue) > self.MAX_HISTORY_LEN:
                queue = queue[-self.MAX_HISTORY_LEN :]


            if len(queue) > self.MAX_BATCH:
                r = queue[:self.MAX_BATCH]
                queue = queue[self.MAX_BATCH:]
            elif len(queue) >= self.MIN_BATCH or time2update or self.__check_last_producer():
                r = queue
                queue = []


            time.sleep(0.05)
            i += 1
            condition.release()
            if r is not None:
                if not (self.sendDB(r)):
                    print("DataBase Error")
                    condition.acquire()
                    queue = r + queue
                    condition.release()


def test():
    def sendDBTest(x):
        MAX_WAIT_TIME = 2.0

        r = random.random()
        if r < 0.3:
            time.sleep(random.random() * 0.1)
            return True
        else:
            wait_time = random.random() * 2.5
            time.sleep(min(MAX_WAIT_TIME, wait_time))
            if MAX_WAIT_TIME < wait_time:
                return False
            else:
                return True

    [ProducerThread(name=str(i)).start() for i in range(10)]
    ConsumerThread(sendDBfn=sendDBTest).start()


if __name__ == "__main__":
    # test()
    pass
