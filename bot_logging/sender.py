import os
import psutil
import datetime

from bot_logging.threading_queue import Singleton


class SenderBase(metaclass=Singleton):
    """
    Used by ConsumerThread to send batched logs from queue
    Singleton like ConsumerThread
    """

    def __init__(self):
        pid = os.getpid()
        process = psutil.Process(pid)
        self.pid = pid
        self.process_name = process.name()

    def send(self, batch_logs):
        """
        Add metadata about process and send datetime and send it by method _send()

        :param batch_logs: [ {'level':level, 'msg':msg, 'event_at':msg_datetime, ‘p_description': logger_name}, ...]
        :return: return True in case of success sending
        """
        data = {
            "post_time": datetime.datetime.utcnow(),
            "pid": self.pid,
            "process_name": self.process_name,
            "logs": batch_logs,
        }
        return self._send(data)

    def _send(self, data):
        raise NotImplementedError()


class ServerSender(SenderBase):
    """Send to server"""

    def __init__(self, user_name, user_token, host):
        """
        :param user_name: auth
        :param user_token: auth
        :param host: ip or url of server
        """
        SenderBase.__init__(self)
        self.user_name = user_name
        self.user_token = user_token
        self.host = host

    def _send(self, data):
        data["user"] = self.user_name
        data["user_token"] = self.user_token
        # TODO: send to server
        return False


class TestSender(SenderBase):
    """
    Send to self.data. Use for tests.
    """

    def __init__(self):
        SenderBase.__init__(self)
        self.data = []

    def _send(self, data):
        self.data.append(data)
        return True
