"""Based on Consumer producer pattern"""

from threading import Thread, Condition
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
            send_message(f'{self.name} {i}')


class ConsumerThread(Thread):
    def __init__(self, sendDBfn, max_batch=30, min_batch=10, max_history_len=200,  **kwargs):
        super(ConsumerThread, self). __init__(**kwargs)
        self.sendDB = sendDBfn
        self.MAX_BATCH = max_batch
        self.MIN_BATCH = min_batch
        self.MAX_HISTORY_LEN = max_history_len

    def run(self):
        global queue
        while True:
            condition.acquire()

            if not queue:
                print("Nothing in queue, consumer is waiting")
                condition.wait()
                print("Producer added something to queue and notified the consumer")

            r = None
            if len(queue) > self.MAX_HISTORY_LEN:
                queue = queue[-self.MAX_HISTORY_LEN:]

            if len(queue) > self.MAX_BATCH:
                r = queue[:self.MAX_BATCH]
                queue = queue[self.MAX_BATCH:]
            elif len(queue) >= self.MIN_BATCH:
                r = queue
                queue = []

            condition.release()

            if r is not None:
                if not(self.sendDB(r)):
                    print('DataBase Error')
                    condition.acquire()
                    queue = r + queue
                    condition.release()
                print(r)




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

if __name__ == '__main__':
    test()