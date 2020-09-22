import os
import psutil
import datetime
import urllib3
import json

from bot_logging.threading_queue import Singleton
from logging import Logger

SEND_LOGS_ENDPOINT = "/send_logs"

logger = Logger("internal_logger")


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
        if len(batch_logs) == 0:
            return True
        data = {
            "data": {
                "post_time": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
                "pid": self.pid,
                "p_name": self.process_name,
                "logs": batch_logs,
            }
        }

        return self._send(data)

    def _send(self, data):
        raise NotImplementedError()


class BadRequestError(Exception):
    """Bad request was provided"""


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
        self.http = urllib3.PoolManager()

    def _send(self, data):
        data["data"]["user"] = self.user_name
        assert (
            len(self.user_token) == 32
        ), f"Length of user_token must be 32 for md5 hashing. len(self.user_token) = {len(self.user_token)}"
        url = "/".join([self.host, SEND_LOGS_ENDPOINT])
        r = self.http.request(
            "POST",
            url,
            body=json.dumps(data),
            headers={
                "Content-Type": "application/json",
                "X-User-Token": self.user_token,
            },
        )
        if r.status == 200:
            return True
        elif r.status == 400:
            raise BadRequestError
        else:
            logger.error("HTTP status " + str(r.status))
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
