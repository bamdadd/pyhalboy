import json

import ramda as r


def objects_to_links(_links):
    return _links or {}


def object_to_resource(_embedded):
    if (not _embedded) or r.is_empty(_embedded):
        return {}
    return list(map(lambda x: object_to_resource(x) if type(x) == list else Resource.from_object(x), _embedded))




class Resource(object):

    def __init__(self) -> None:
        super().__init__()
        self.links = {}

    def from_object(body):
        object = json.loads(body)
        _links = object["_links"]
        _embedded = object["_embedded"]
        properties = object

        return Resource() \
            .add_links(objects_to_links(_links)) \
            .add_resources(object_to_resource(_embedded)) \
            .add_properties(properties)

    def get_href(self, href):
        pass

    def _add_link(self, resource, re_value):
        rel = re_value[0]
        value = re_value[1]

    def _create_or_append(self, coll, rel, value):
        if not (rel in coll):
            coll[rel] = value
            return coll
        coll[rel] = [coll[rel], value]
        return coll

    def add_link(self, rel, value):
        if r.is_empty(value):
            return self
        if type(value) == str:
            return self.add_link(rel, {'href': value})
        self.links = self._create_or_append(self.links.copy(), rel, value)
        return self

    def get_link(self, rel):
        return self.links[rel]

    def add_links(self, coll):
        self.apply_to_resource(coll, self._add_link)
        return self

    def _add_to_resource(self, resources, k, v):
        # (lambda resource, kv: resource.add_resoruce(r.to_pairs(kv)))
        return resources.add_resource()

    def add_resources(self, resources):
        # return self.apply_to_resource(self,
        #                               resoruces,
        #                               )
        return self

    def apply_to_resource(self, coll, fn):
        return r.reduce(fn, self, r.to_pairs(coll))

    def add_properties(self, properties):
        return self
