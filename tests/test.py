from unittest import TestCase

from bot_logging import TelegramLogger
from time import time, sleep
import random
from threading import Thread

from utils import TestSender

def multiprocessing_test():
    pass


def get_logger_funcs(logger):
    funcs = [logger.debug, logger.info, logger.warning, logger.error, logger.critical]
    funcs = [
        lambda postfix: logger.debug('This is a debug message' + postfix),
        lambda postfix: logger.info('This is an info message' + postfix),
        lambda postfix: logger.warning('This is a warning message' + postfix),
        lambda postfix: logger.error('This is an error message' + postfix),
        lambda postfix: logger.critical('This is a critical message' + postfix)
    ]
    return funcs

def thread_func(sec_for_test):
    start_time = time()
    sender = TestSender()
    logger = TelegramLogger('test_process', sender=sender)
    funcs = get_logger_funcs(logger)
    i = 0
    while True:
        func = funcs[i % len(funcs)]
        func('')
        i += 1

        wait_time = random.random() * 0.01
        if time() - start_time + wait_time >= sec_for_test:
            break
        sleep(wait_time)


class Test(TestCase):
    def test(self):
        THREAD_NUM = 5
        threads = []
        for i in range(THREAD_NUM):
            x = Thread(target=thread_func, args=(2.0,))
            x.start()
            threads.append(x)
        for thread in threads:
            thread.join()