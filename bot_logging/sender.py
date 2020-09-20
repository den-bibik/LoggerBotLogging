import requests


class ServerSender:
    def __init__(self, user_name, user_token, host):
        self.user_name = user_name
        self.user_token = user_token
        self.host = host

    def send(self, data):
        pass