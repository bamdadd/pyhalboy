import requests
from resource import Resource



class Navigator:
    def __init__(self, options={}):
        self.options = options
        self._status_code = None
        self._location = None
        self._resource = None

    def discover(self, url, options={}):
        return Navigator(options).get_url(url, {}, {})

    def get_url(self, url, params, config):
        response = requests.get(url)
        self._status_code = response.status_code
        self._location = response.url
        self._resource = Resource.from_object(response.content)
        return self

    def resource(self):
        return self._resource

    def status(self):
        return self._status_code
