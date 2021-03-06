import concurrent.futures
from time import time, sleep
from unittest import TestCase

from bot_logging import RemoteLogger
from bot_logging.sender import TestSender
from bot_logging.tests.utils import get_logger_funcs
from bot_logging.threading_queue import Singleton


class LoggerLevelTest(TestCase):
    @staticmethod
    def _test_level(level):
        Singleton.clear_instances()
        sender = TestSender()

        def run(sender):
            logger = RemoteLogger(
                "test_process", sender=sender, level=level, max_history_len=1e9
            )
            for func in get_logger_funcs(logger):
                func("")

        run(sender)
        min_level = 50
        for batch in sender.data:
            for log in batch["data"]["logs"]:
                min_level = min(log["level"], min_level)
        assert min_level == level, f"min_level = {min_level}, level = {level}"

    def test(self):
        for level in [30, 40, 50]:
            self._test_level(level)


class MultiThreadingTest(TestCase):
    @staticmethod
    def _check_log_results_multitheread(logged_batches, threads_log):
        logged_thread = [[] for _ in threads_log]
        for batch in logged_batches:
            for log in batch["data"]["logs"]:
                thread_id = int(log["p_description"].split("_")[-1])
                logged_thread[thread_id].append(log)

        for result, target in zip(logged_thread, threads_log):
            assert len(result) == len(
                target
            ), f"missed some logs {len(result)} != {len(target)}"
            # print(f"In thread {i} len(result)={len(result)} len(target)={len(target)}")

        return True

    @staticmethod
    def _thread_func(sec_for_test, sender, thread_name):
        start_time = time()
        logger = RemoteLogger(
            "test_process_" + thread_name, sender=sender, max_history_len=1e9
        )
        funcs = get_logger_funcs(logger)
        i = 0
        results = []
        while True:
            func = funcs[i % len(funcs)]
            result = func("")
            results.append(result)
            i += 1

            wait_time = 0.001
            if time() - start_time + wait_time >= sec_for_test:
                break
            sleep(wait_time)

        return results

    def test(self):
        Singleton.clear_instances()
        thread_num = 100
        threads = []
        thread_res = []
        sender = TestSender()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for i in range(thread_num):
                thread = executor.submit(
                    self._thread_func, 2.0, sender, "thread_" + str(i)
                )
                threads.append(thread)
            thread_res = []
            for thread in threads:
                res = thread.result()
                thread_res.append(res)

        self._check_log_results_multitheread(sender.data, thread_res)
