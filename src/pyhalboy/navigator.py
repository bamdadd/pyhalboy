from .resource import Resource

import ramda as r
import requests
import uri
from uritemplate import URITemplate


def resolve_link(templated_url, params):
    template = URITemplate(templated_url)
    variables = template.variables
    # variables = template.parts.reduce((accumulator, part) => {
    # if not r.is_empty(part.variables):
    #     return r.concat(part.variables.map(variable => variable.name), accumulator)
    #
    # return accumulator
    # }, [])
    url = template.expand(params)
    query_object = uri.URI(url)
    full_params = params
    # full_params = r.merge(r.omit(variables, params), query_object)
    # url_without_query_string = URI(url).query('').toString()

    return {
        'href': url,
        'params': full_params
    }


def make_absolute(base, href):
    return requests.compat.urljoin(base, href)


class Navigator:
    def __init__(self, options={}):
        self.options = options
        self._status_code = None
        self._location = None
        self._resource = None
        self._response = None

    @staticmethod
    def discover(url, options={}):
        return Navigator(options).get_url(url, {}, {})

    def get_url(self, url, params, config):
        response = requests.get(url)
        self._status_code = response.status_code
        self._location = response.url
        self._response = response
        self._resource = Resource.from_object(response.json())
        return self

    def post_url(self, url, body, params, config):
        response = requests.post(url, json=body)
        self._status_code = response.status_code
        self._response = response
        self._location = response.url
        self._resource = Resource.from_object(response.json())
        return self

    def resource(self):
        return self._resource

    def status(self):
        return self._status_code

    def get_header(self, key):
        return self._response.headers[key]

    def _resolve_link(self, rel, params):
        relative_href = self._resource.get_href(rel)
        if (r.is_empty(relative_href)):
            raise RuntimeError('Attempting to follow the link "{}", which does not exist')
        link = resolve_link(relative_href, params)
        return {
            'href': make_absolute(self._location, link['href']),
            'query_params': link['params']
        }

    def get(self, rel, params={}, config={}):
        link = self._resolve_link(rel, params)
        return self.get_url(link['href'], link['query_params'], config)

    def post(self, rel, body, params={}, config={}):
        link = self._resolve_link(rel, params)
        return self.post_url(link['href'], body, link['query_params'], config)
