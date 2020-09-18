import threading
import time
import json

data = []


def thread_reader():
    while True:
        time.sleep(2)
        with open("thread.log", "w") as f:
            data_thread = data
            data = []
            json.dump(data_thread, f)


def main():
    i = 0
    x = threading.Thread(target=thread_reader)
    x.start()
    while True:
        time.sleep(0.1)
        data.append(i)
        i += 1
        with open("main.log", "w") as f:
            json.dump(data, f)


if __name__ == "__main__":
    main()
