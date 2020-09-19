import requests


class ServerSender:
    def __init__(self, credientals=None):
        if credientals is not None and "url" in credientals:
            self.url = credientals["url"]

    def send(self, data):
        r = requests.post(self.url)
