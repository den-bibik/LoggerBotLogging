from unittest import TestCase

from bot_logging import RemoteLogger
from time import time, sleep
import concurrent.futures

from bot_logging.sender import TestSender
from datetime import datetime



def get_logger_funcs(logger):
    func_dict = {
        # "debug": logger.debug,
        # "info": logger.info,
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
    logger = RemoteLogger("test_process_" + thread_name, sender=sender, max_history_len=1e9)
    funcs = get_logger_funcs(logger)
    i = 0
    results = []
    while True:
        func = funcs[i % len(funcs)]
        result = func("")
        results.append(result)
        i += 1

        wait_time = 0.0
        if time() - start_time + wait_time >= sec_for_test:
            break
        sleep(wait_time)

    return results


def check_log_results_multitheread(logged_batches, threads_log):
    logged_thread = [[] for _ in threads_log]
    for batch in logged_batches:
        for log in batch["logs"]:
            thread_id = int(log["p_name"].split("_")[-1])
            logged_thread[thread_id].append(log)

    for i, (result, target) in enumerate(zip(logged_thread, threads_log)):
        assert len(result) == len(target), f"missed some logs {len(result)} != {len(target)}"
        print(f"In thread {i} len(result)={len(result)} len(target)={len(target)}")

    return True


class Test(TestCase):
    def test(self):
        THREAD_NUM = 100
        threads = []
        thread_res = []
        sender = TestSender()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for i in range(THREAD_NUM):
                thread = executor.submit(thread_func, 2.0, sender, "thread_" + str(i))
                threads.append(thread)
            thread_res = []
            for thread in threads:
                res = thread.result()
                thread_res.append(res)

        assert check_log_results_multitheread(sender.data, thread_res)
