"""Based on Consumer producer pattern"""
import threading
from threading import Thread, Condition
from wrapt import synchronized
from logging import Handler
import time
import datetime

queue = []
condition = Condition()
lock = threading.Lock()


class ProducerHandler(Handler):
    """
    Send message to ConsumerThread throw shared queue
    Used as handler in Logger
    """

    def __init__(
        self,
        sender,
        logger_name,
        max_batch,
        min_batch,
        max_history_len,
        max_time2update,
        *args,
        **kwargs,
    ):
        Handler.__init__(self, *args, **kwargs)
        self.logger_name = logger_name
        self.consumer = ConsumerThread(
            sender,
            max_batch=max_batch,
            min_batch=min_batch,
            max_history_len=max_history_len,
            max_time2update=max_time2update
        )
        self.consumer.add_producer()
        self.lock = condition
        global queue
        self.queue = queue

    def emit(self, record):
        message = {
            "level": record.levelno,
            "event_at": datetime.datetime.utcnow(),
            "msg": record.msg,
            "p_name": self.logger_name,
        }
        queue.append(message)

    def release(self):
        self.lock.notify()
        self.lock.release()

    def __del__(self):
        last_producer = self.consumer.del_producer()
        if last_producer:
            self.consumer.join()


class Singleton(type):
    """
    From https://stackoverflow.com/questions/50566934
    We need only one ConsumerThread and ServerSender
    """

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
    """
    Take data from shared queue and send by self.sender

    Methods:
        run - main cycle in Thread
        add_producer - you need call it on every new producer created
        del_producer - you need call it on every producer deleted.
                    Thread will ended only when last producer will be deleted.
    """

    def __init__(
        self,
        sender,
        max_batch,
        min_batch,
        max_history_len,
        max_time2update,
        **kwargs,
    ):
        super(ConsumerThread, self).__init__(**kwargs)
        self.sender = sender
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
        last_producer = self._producer_number == 0
        self.mutex_producer_number.release()
        return last_producer

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
                print("Producer added something to queue and notified the consumer")

            r = None
            if len(queue) == 0:
                previous_iter_empty_queue = True
            elif previous_iter_empty_queue:
                previous_iter_empty_queue = False
                last_time_one_added = time.time()

            time2update = time.time() - last_time_one_added > self.MAX_TIME2UPDATE
            if len(queue) > self.MAX_HISTORY_LEN:
                queue = queue[-self.MAX_HISTORY_LEN :]

            if len(queue) > self.MAX_BATCH:
                r = queue[: self.MAX_BATCH]
                queue = queue[self.MAX_BATCH :]
            elif (
                len(queue) >= self.MIN_BATCH
                or time2update
                or self.__check_last_producer()
            ):
                r = queue
                queue = []
            condition.release()

            if not (len(queue) > self.MAX_BATCH):
                time.sleep(0.1)

            i += 1
            if r is not None:
                if not (self.sender.send(r)):
                    print("DataBase Error")
                    condition.acquire()
                    queue = r + queue
                    condition.release()
                else:
                    r = None


# def test():
#     def sendDBTest(x):
#         MAX_WAIT_TIME = 2.0
#
#         r = random.random()
#         if r < 0.3:
#             time.sleep(random.random() * 0.1)
#             return True
#         else:
#             wait_time = random.random() * 2.5
#             time.sleep(min(MAX_WAIT_TIME, wait_time))
#             if MAX_WAIT_TIME < wait_time:
#                 return False
#             else:
#                 return True
#
#     [ProducerThread(name=str(i)).start() for i in range(10)]
#     ConsumerThread(sendDBfn=sendDBTest).start()


if __name__ == "__main__":
    # test()
    pass
