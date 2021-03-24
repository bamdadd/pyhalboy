import functools as f
import json

import ramda as r


def objects_to_links(_links):
    return _links or {}


def object_to_resource(_embedded):
    if (not _embedded) or r.is_empty(_embedded):
        return {}
    result = {}
    for k in _embedded.keys():
        result[k] = list(map(lambda x: object_to_resource(x) if type(x) == list else Resource.from_object(x), _embedded[k]))
    return result


def links_to_object(links):
    if r.is_empty(links):
        return {}
    return {"_links": links}


def resources_to_object(resources):
    if r.is_empty(resources):
        return {}
    coll = resources.copy()

    for k in coll.keys():
        if type(coll[k]) == list:
            coll[k] = (list(map(lambda x: x.to_object(), resources[k])))
        else:
            coll[k] = coll[k].to_object()
    return {"_embedded": coll}


class Resource(object):

    def __init__(self) -> None:
        super().__init__()
        self.properties = {}
        self.links = {}
        self.embedded = {}

    def from_object(body):
        if type(body) == str or type(body) == bytes:
            object = json.loads(body)
        elif type(body) == dict:
            object = body
        else:
            raise RuntimeError("unknow type {} for {}".format(type(body), body))
        _links = object.get("_links")
        _embedded = object.get("_embedded")
        properties = {k: object[k] for k in object.keys() if k not in ['_links', '_embedded']}

        return Resource() \
            .add_links(objects_to_links(_links)) \
            .add_properties(properties) \
            .add_resources(object_to_resource(_embedded))

    def get_href(self, rel):

        return self.links[rel]['href']

    def _create_or_append(self, coll, rel, value):
        if not (rel in coll):
            coll[rel] = value
            return coll
        if type(coll[rel]) == list:
            coll[rel] = r.flatten([coll[rel], value])
            return coll
        coll[rel] = [coll[rel], value]
        return coll

    def add_link(self, rel, value):
        if not value or r.is_nil(value) or r.is_empty(value):
            return self
        if type(value) == str:
            return self.add_link(rel, {'href': value})
        self.links = self._create_or_append(self.links.copy(), rel, value)
        return self

    def get_link(self, rel):
        return self.links[rel]

    def get_hrefs(self):
        return f.reduce(lambda acc, x: {**acc, x[0]: x[1]["href"]}, r.to_pairs(self.links), {})

    def get_links(self):
        return self.links

    def add_links(self, coll):
        list(map(lambda pair: self.add_link(pair[0], pair[1]), (r.to_pairs(coll))))
        return self

    def add_resources(self, coll):
        if not r.is_empty(coll):
            list(map(lambda pair: self.add_resource(pair[0], pair[1]), (r.to_pairs(coll))))
        return self

    def get_resources(self):
        return resources_to_object(self.embedded).get('_embedded')

    def get_resource(self, key):
        return self.embedded[key]

    def add_resource(self, rel, value):
        if not value or r.is_nil(value) or r.is_empty(value):
            return self
        self.embedded = self._create_or_append(self.embedded.copy(), rel, value)
        return self

    def apply_to_resource(self, coll, fn):
        return r.reduce(fn, self, r.to_pairs(coll))

    def add_property(self, key, value):
        self.properties[key] = value
        return self

    def get_property(self, key):
        return self.properties[key]

    def get_properties(self):
        return self.properties

    def add_properties(self, coll):
        list(map(lambda pair: self.add_property(pair[0], pair[1]), (r.to_pairs(coll))))
        return self

    def to_object(self):
        return r.merge(r.merge({**self.properties}, links_to_object(self.links)), resources_to_object(self.embedded))
