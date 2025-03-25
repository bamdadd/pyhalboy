from typing import (
    Any,
    Callable,
    NotRequired,
    Self,
    TypedDict,
    cast,
)
from collections.abc import Mapping, Sequence

from .types import (
    Href,
    LinkRel,
    PropertyName,
    PropertyValue,
    Properties,
    ResourceRel,
)


class LinkDict(TypedDict):
    href: Href
    title: NotRequired[str]
    templated: NotRequired[bool]


# This requires https://peps.python.org/pep-0728
# class ResourceDict(TypedDict, extra_items=JSONNode):
#     _links: Mapping[LinkRel, LinkDict | Sequence[LinkDict]]
#     _embedded: Mapping[ResourceRel, Self | Sequence[Self]]

ResourceDict = Mapping[str, Any]


class EmbeddedPropertyDict(TypedDict):
    _embedded: NotRequired[
        Mapping[ResourceRel, ResourceDict | Sequence[ResourceDict]]
    ]


class LinksPropertyDict(TypedDict):
    _links: NotRequired[Mapping[LinkRel, LinkDict | Sequence[LinkDict]]]


def dict_to_resource(resource_dict: ResourceDict) -> "Resource":
    _links = resource_dict.get("_links", {})
    _embedded = resource_dict.get("_embedded", {})
    _properties = {
        prop: resource_dict[prop]
        for prop in resource_dict.keys()
        if prop not in ["_links", "_embedded"]
    }

    return (
        Resource()
        .add_links(_links)
        .add_properties(_properties)
        .add_resources(dict_to_embedded(_embedded))
    )


def dicts_to_resources(
    resource_dicts: ResourceDict | Sequence[ResourceDict],
) -> "Resource | Sequence[Resource]":
    if isinstance(resource_dicts, Sequence):
        return [
            dict_to_resource(resource_dict) for resource_dict in resource_dicts
        ]
    return dict_to_resource(resource_dicts)


def dict_to_embedded(
    embeds_dict: Mapping[ResourceRel, ResourceDict | Sequence[ResourceDict]],
) -> dict[ResourceRel, "Resource | Sequence[Resource]"]:
    if len(embeds_dict) == 0:
        return {}

    return {
        rel: dicts_to_resources(embeds_dict[rel]) for rel in embeds_dict.keys()
    }


def links_to_object(
    links: dict[LinkRel, LinkDict | Sequence[LinkDict]],
) -> LinksPropertyDict:
    if len(links) == 0:
        return {}
    return {"_links": links}


def resources_to_object(
    resources: "Resource | Sequence[Resource]",
) -> ResourceDict | Sequence[ResourceDict]:
    if isinstance(resources, Sequence):
        return [resource.to_object() for resource in resources]
    return resources.to_object()


def embedded_to_object(
    embeds: dict[ResourceRel, "Resource | Sequence[Resource]"],
) -> EmbeddedPropertyDict:
    if len(embeds) == 0:
        return {}

    return {
        "_embedded": {
            rel: resources_to_object(embeds[rel]) for rel in embeds.keys()
        }
    }


def create_or_append[R: (LinkRel, ResourceRel), T: (LinkDict, "Resource")](
    links: dict[R, T | Sequence[T]], rel: R, value: T | Sequence[T]
) -> dict[R, T | Sequence[T]]:
    if rel not in links:
        links[rel] = value
        return links

    link = links[rel]

    if isinstance(link, Sequence) and isinstance(value, Sequence):
        links[rel] = [*link, *value]
    elif isinstance(link, Sequence):
        links[rel] = [*link, cast(T, value)]
    else:
        links[rel] = [cast(T, link), cast(T, value)]

    return links


class Resource(object):
    _links: dict[LinkRel, LinkDict | Sequence[LinkDict]]
    _embedded: dict[ResourceRel, "Resource | Sequence[Resource]"]
    _properties: dict[PropertyName, PropertyValue]

    def __init__(
        self,
        properties: Mapping[PropertyName, PropertyValue] = {},
        links: Mapping[LinkRel, LinkDict | Sequence[LinkDict]] = {},
        embedded: Mapping[PropertyName, Self | Sequence[Self]] = {},
    ) -> None:
        self._properties = dict(properties)
        self._links = dict(links)
        self._embedded = dict(embedded)

    @staticmethod
    def from_object(resource_dict: ResourceDict):
        return dict_to_resource(resource_dict)

    def get_href(self, rel: LinkRel) -> Href | Sequence[Href]:
        link_or_links = self._links[rel]

        if isinstance(link_or_links, Sequence):
            return [link["href"] for link in link_or_links]

        return link_or_links["href"]

    def add_link(self, rel: LinkRel, value: LinkDict | Href) -> Self:
        if isinstance(value, Href):
            return self.add_link(rel, {"href": value})

        self._links = create_or_append(self._links, rel, value)

        return self

    def get_link(self, rel: LinkRel) -> LinkDict | Sequence[LinkDict]:
        link_or_links = self._links[rel]

        if isinstance(link_or_links, Sequence):
            return list(link_or_links)

        return link_or_links

    def get_hrefs(self) -> Mapping[LinkRel, Href | Sequence[Href]]:
        return {rel: self.get_href(rel) for rel in self._links}

    def get_links(self) -> Mapping[LinkRel, LinkDict | Sequence[LinkDict]]:
        return dict(self._links)

    def add_links(
        self,
        links: Mapping[LinkRel, Href | LinkDict | Sequence[LinkDict]],
    ) -> Self:
        for rel, value in links.items():
            if isinstance(value, Href) or isinstance(value, dict):
                self.add_link(rel, value)
            else:
                for link in value:
                    self.add_link(rel, link)

        return self

    def add_resources(
        self, embeds: Mapping[ResourceRel, Self | Sequence[Self]]
    ) -> Self:
        for rel in embeds:
            self.add_resource(rel, embeds[rel])

        return self

    def get_resources(
        self,
    ) -> Mapping[ResourceRel, "Resource | Sequence[Resource]"]:
        return dict(self._embedded)

    def get_resource(
        self, rel: ResourceRel
    ) -> "Resource | Sequence[Resource]":
        resource_or_resources = self._embedded[rel]

        if isinstance(resource_or_resources, Sequence):
            return list(resource_or_resources)

        return resource_or_resources

    def add_resource(
        self, rel: ResourceRel, value: Self | Sequence[Self]
    ) -> Self:
        self._embedded = create_or_append(self._embedded, rel, value)
        return self

    def apply_to_resource[
        R: (LinkRel, ResourceRel, PropertyName),
        V: (LinkDict, "Resource", PropertyValue),
    ](
        self,
        items: Mapping[R, V],
        fn: Callable[["Resource", R, V], "Resource"],
    ) -> "Resource":
        slf = self
        for rel, value in items.items():
            slf = fn(slf, rel, value)
        return slf

    def add_property(self, key: PropertyName, value: PropertyValue):
        self._properties[key] = value
        return self

    def get_property(self, name: PropertyName) -> PropertyValue:
        return self._properties[name]

    def get_properties(self) -> Properties:
        return dict(self._properties)

    def add_properties(self, properties: Properties) -> Self:
        for property, value in properties.items():
            self.add_property(property, value)

        return self

    def to_object(self) -> ResourceDict:
        links = links_to_object(self._links)
        embedded = embedded_to_object(self._embedded)

        return {**links, **self._properties, **embedded}
