from urllib import parse as urllib

from typing import TypedDict, NotRequired
from dataclasses import dataclass
from collections.abc import Mapping

from httpx import Client, Response
from uritemplate import URITemplate

from .types import Href, LinkRel, StatusCode, JSONNode
from .resource import Resource


class HttpSettingsDict(TypedDict):
    headers: NotRequired[dict[str, str]]


class SettingsDict(TypedDict):
    http: NotRequired[HttpSettingsDict]
    client: NotRequired[Client]


@dataclass
class HttpSettings(object):
    headers: dict[str, str]


@dataclass
class Settings(object):
    http: HttpSettings
    client: Client


def _resolve_link(
    href_template: Href, params: Mapping[str, str] | None = None
) -> tuple[str, Mapping[str, str]]:
    resolved_params: Mapping[str, str] = params if params is not None else {}
    template = URITemplate(href_template)
    # variables = template.variables
    # variables = template.parts.reduce((accumulator, part) => {
    # if not r.is_empty(part.variables):
    #     return r.concat(
    #         part.variables.map(variable => variable.name), accumulator
    #     )
    #
    # return accumulator
    # }, [])
    href = template.expand(var_dict=None, **resolved_params)
    # query_object = uri.URI(url)
    full_params = resolved_params
    # full_params = r.merge(r.omit(variables, params), query_object)
    # url_without_query_string = URI(url).query('').toString()

    return href, full_params


def _make_absolute(base: str, href: Href) -> Href:
    return urllib.urljoin(base, href)


def _default_settings() -> Settings:
    return Settings(
        http=HttpSettings(headers={}),
        client=Client(),
    )


def _resolve_settings(
    settings: Settings, overrides: SettingsDict | None = None
) -> Settings:
    if overrides is None:
        return settings

    return Settings(
        http=HttpSettings(
            headers={
                **settings.http.headers,
                **overrides.get("http", {}).get("headers", {}),
            },
        ),
        client=overrides.get("client", settings.client),
    )


def _get_url(
    *,
    url: Href,
    params: Mapping[str, str] | None = None,
    settings: Settings,
) -> Response:
    return settings.client.get(url, params=params)


def _post_url(
    *,
    url: Href,
    body: JSONNode,
    params: Mapping[str, str] | None = None,
    settings: Settings,
):
    return settings.client.post(url, json=body, params=params)


class Navigator:
    _settings: Settings
    _status_code: StatusCode
    _location: Href
    _resource: Resource
    _response: Response

    def __init__(
        self,
        settings: Settings,
        response: Response,
    ):
        self._settings = settings
        self._response = response
        self._status_code = response.status_code
        self._location = str(response.url)
        self._resource = Resource.from_object(response.json())

    @staticmethod
    def discover(url: Href, settings: SettingsDict = {}):
        resolved_settings = _resolve_settings(_default_settings(), settings)

        response = _get_url(url=url, params={}, settings=resolved_settings)

        return Navigator(settings=resolved_settings, response=response)

    def resource(self) -> Resource:
        return self._resource

    def status(self):
        return self._status_code

    def get_header(self, header: str):
        return self._response.headers[header]

    def _resolve_link(
        self,
        *,
        rel: LinkRel,
        index: int = 0,
        params: Mapping[str, str] | None = None,
    ) -> tuple[str, Mapping[str, str]]:
        href = self._resource.get_href(rel)

        if not isinstance(href, Href):
            href = href[index]

        # if r.is_empty(href):
        #     raise RuntimeError(
        #         'Attempting to follow the link "{}", which does not exist'
        #     )

        href, resolved_params = _resolve_link(href, params)

        return _make_absolute(self._location, href), resolved_params

    def get(
        self, rel: LinkRel, params: Mapping[str, str] | None = None
    ) -> "Navigator":
        href, resolved_params = self._resolve_link(rel=rel, params=params)

        return Navigator(
            settings=self._settings,
            response=_get_url(
                url=href, params=resolved_params, settings=self._settings
            ),
        )

    def post(
        self,
        rel: LinkRel,
        body: JSONNode,
        params: Mapping[str, str] | None = None,
    ):
        href, resolved_params = self._resolve_link(rel=rel, params=params)

        return Navigator(
            settings=self._settings,
            response=_post_url(
                url=href,
                body=body,
                params=resolved_params,
                settings=self._settings,
            ),
        )
