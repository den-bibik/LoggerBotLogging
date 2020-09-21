"""Based on Consumer Producer pattern"""
import threading
from threading import Thread, Condition
from logging import Handler
import time
import datetime
from wrapt import synchronized


queue = []
condition = Condition()
lock = threading.Lock()


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
        max_time_to_update,
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
            max_time_to_update=max_time_to_update,
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
        max_time_to_update,
        **kwargs,
    ):
        Thread.__init__(self, **kwargs)
        self.sender = sender
        self.MAX_BATCH = max_batch
        self.MIN_BATCH = min_batch
        self.MAX_HISTORY_LEN = max_history_len
        self.MAX_TIME_TO_UPDATE = max_time_to_update
        self._producer_number = 1
        self._first_producer = True
        self.mutex_producer_number = threading.Lock()
        self.start()

    def __check_no_producers(self):
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
                if self.__check_no_producers():
                    break
                print("Producer added something to queue and notified the consumer")

            bacth_to_send = None
            if len(queue) == 0:
                previous_iter_empty_queue = True
            elif previous_iter_empty_queue:
                previous_iter_empty_queue = False
                last_time_one_added = time.time()

            time2update = time.time() - last_time_one_added > self.MAX_TIME_TO_UPDATE
            if len(queue) > self.MAX_HISTORY_LEN:
                queue = queue[-self.MAX_HISTORY_LEN :]

            if len(queue) > self.MAX_BATCH:
                bacth_to_send = queue[: self.MAX_BATCH]
                queue = queue[self.MAX_BATCH :]
            elif (
                len(queue) >= self.MIN_BATCH
                or time2update
                or self.__check_no_producers()
            ):
                bacth_to_send = queue
                queue = []
            condition.release()

            if not (len(queue) > self.MAX_BATCH):
                time.sleep(0.1)

            i += 1
            if bacth_to_send is not None:
                if not (self.sender.send(bacth_to_send)):
                    print("DataBase Error")
                    condition.acquire()
                    queue = bacth_to_send + queue
                    condition.release()
                else:
                    bacth_to_send = None