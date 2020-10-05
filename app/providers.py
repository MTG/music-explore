from abc import ABC, abstractmethod
from flask import url_for

class AudioProvider(ABC):
    @abstractmethod
    def get_uri(self, track_id):
        pass


class JamendoProvider(AudioProvider):
    def __init__(self, client_id):
        if not client_id:
            raise RuntimeError('Empty Jamendo client ID')
        self.client_id = client_id

    def get_uri(self, track_id):
        return f'https://mp3l.jamendo.com/?trackid={track_id}&format=mp31&from=app-{self.client_id}'


class LocalProvider(AudioProvider):
    def get

    def get_uri(self, track_id):
        return url_for('static', filename=f'audio/.mp3')

def init_app(app):
