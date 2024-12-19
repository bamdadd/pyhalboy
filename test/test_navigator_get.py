import sys
import pytest

from collections.abc import Sequence

import httpx
import respx

from pyhalboy.resource import Resource
from pyhalboy.navigator import Navigator


def create_user(id, name):
    return (
        Resource()
        .add_link("self", "/users/{}".format(id))
        .add_property("name", name)
        .add_property("id", id)
    )


class TestNavigatorGet(object):
    def test_get(self):
        router = respx.Router(base_url="http://test.com")
        router.get("/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "_links": {"users": {"href": "/users"}},
                    "_embedded": {},
                    "prop1": 1,
                },
            )
        )
        router.get("/users").mock(
            return_value=httpx.Response(
                200,
                json=(
                    Resource()
                    .add_property("test", 1)
                    .add_link("self", "http://test.com/users")
                    .add_resource(
                        "users",
                        [
                            create_user("fred", "Fred"),
                            create_user("sue", "Sue"),
                            create_user("mary", "Mary"),
                        ],
                    )
                    .to_object()
                ),
            )
        )
        client = httpx.Client(
            transport=httpx.MockTransport(handler=router.handler)
        )

        headers = {"authorization": "some-token"}
        navigator = Navigator.discover(
            "http://test.com/",
            settings={"client": client, "http": {"headers": headers}},
        )

        result = navigator.get("users")
        assert result.status() == 200

        users = result.resource().get_resource("users")
        assert isinstance(users, Sequence)

        names = [u.get_property("name") for u in users]

        assert names == ["Fred", "Sue", "Mary"]
        assert result.resource().get_property("test") == 1
        assert result.resource().get_href("self") == "http://test.com/users"

    def test_get_with_params(self):
        router = respx.Router(base_url="http://test.com")
        router.get("/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "_links": {
                        "user": {"href": "/users/{userId}", "templated": True}
                    },
                },
            )
        )
        router.get("/users/fred").mock(
            return_value=httpx.Response(
                200,
                json=create_user("fred", "Fred").to_object(),
            )
        )
        client = httpx.Client(
            transport=httpx.MockTransport(handler=router.handler)
        )

        navigator = Navigator.discover(
            "http://test.com", settings={"client": client}
        )

        result = navigator.get("user", {"userId": "fred"})

        assert result.status() == 200
        assert result.resource().get_property("name") == "Fred"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
