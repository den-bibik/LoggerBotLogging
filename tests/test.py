from unittest import TestCase

from bot_logging import RemoteLogger
from time import time, sleep
import random
from threading import Thread
import concurrent.futures

from utils import TestSender
from datetime import datetime

def multiprocessing_test():
    pass


def get_logger_funcs(logger):
    func_dict = {
        "debug": logger.debug,
        "info": logger.info,
        "warning": logger.warning,
        "error": logger.error,
        "critical": logger.critical,
    }

    def get_test_func(key, func):
        def test_func(postfix):
            dt = datetime.now()
            message = "This is a " + key + " message" + postfix
            func(message)
            return message, dt
        return test_func

    funcs = [get_test_func(k, func_dict[k]) for k in func_dict]
    return funcs


def thread_func(sec_for_test, sender, thread_name):
    start_time = time()
    logger = RemoteLogger("test_process_" + thread_name, sender=sender)
    funcs = get_logger_funcs(logger)
    i = 0
    results = []
    while True:
        func = funcs[i % len(funcs)]
        result = func("")
        results.append(result)
        i += 1

        wait_time = 0#random.random() * 0.001
        if time() - start_time + wait_time >= sec_for_test:
            break
        sleep(wait_time)

    return results



def check_log_results_multitheread(logged_batches, threads_log):
    thread = threads_log[0]
    batch = logged_batches[0]



class Test(TestCase):
    def test(self):
        THREAD_NUM = 5
        threads = []
        thread_res = []
        sender = TestSender()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for i in range(THREAD_NUM):
                thread = executor.submit(thread_func, 2.0, sender, 'thread_' + str(i))
                threads.append(thread)
            thread_res = []
            for thread in threads:
                res = thread.result()
                thread_res.append(res)

        data = sender.data
        print(len(data))


