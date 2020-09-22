"""Based on Consumer Producer pattern"""
import datetime
import threading
import time
from logging import Handler, Logger
from threading import Thread, Condition

from wrapt import synchronized

QUEUE = []
condition = Condition()
lock = threading.Lock()

DISPLAY = False
logger = Logger("internal_logger")

MAX_SEND_ATTEMPT = 1


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

    @staticmethod
    def clear_instances():
        Singleton._instances = {}


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

        if self.level < 30:
            logger.warning("Level was %s < 30. Level set to 30.", self.level)
            self.level = 30

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
        global QUEUE
        self.queue = QUEUE

    def emit(self, record):
        message = {
            "level": record.levelno,
            "event_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
            "msg": record.msg,
            "p_description": self.logger_name,
        }
        QUEUE.append(message)

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
        self.max_batch = max_batch
        self.min_batch = min_batch
        self.max_history_len = max_history_len
        self.max_time_to_update = max_time_to_update
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

    def del_all_producers(self):
        self.mutex_producer_number.acquire()
        self._producer_number = 0
        last_producer = True
        self.mutex_producer_number.release()
        return last_producer

    def run(self):
        global QUEUE
        previous_iter_empty_queue = True
        last_time_one_added = -1
        i = 0
        send_attemnpt = 0
        while True:
            if DISPLAY:
                print("self._producer_number", self._producer_number)
            condition.acquire()
            if not QUEUE:
                if DISPLAY:
                    print("Nothing in queue, consumer is waiting")
                if self.__check_no_producers():
                    condition.release()
                    break
                if DISPLAY:
                    print("Producer added something to queue and notified the consumer")

            bacth_to_send = None
            if len(QUEUE) == 0:
                previous_iter_empty_queue = True
            elif previous_iter_empty_queue:
                previous_iter_empty_queue = False
                last_time_one_added = time.time()

            time2update = time.time() - last_time_one_added > self.max_time_to_update
            if len(QUEUE) > self.max_history_len:
                QUEUE = QUEUE[-self.max_history_len:]

            if len(QUEUE) > self.max_batch:
                bacth_to_send = QUEUE[: self.max_batch]
                QUEUE = QUEUE[self.max_batch:]
            elif (
                    len(QUEUE) >= self.min_batch
                    or time2update
                    or self.__check_no_producers()
            ):
                bacth_to_send = QUEUE
                QUEUE = []
            condition.release()

            if len(QUEUE) <= self.max_batch:
                time.sleep(0.1)

            i += 1
            if bacth_to_send is not None:
                if self.sender.send(bacth_to_send) or send_attemnpt >= MAX_SEND_ATTEMPT:
                    send_attemnpt = 0
                    bacth_to_send = None
                else:
                    send_attemnpt += 1
                    if DISPLAY:
                        print("DataBase Error")
                    condition.acquire()
                    QUEUE = bacth_to_send + QUEUE
                    condition.release()
                    time.sleep(1.0)
