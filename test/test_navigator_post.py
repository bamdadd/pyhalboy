import sys
import pytest


import httpx
import respx

from pyhalboy.resource import Resource
from pyhalboy.navigator import Navigator


def create_user(id, name):
    return (
        Resource()
        .add_link("self", "/users/{}".format(id))
        .add_property("name", name)
    )


class TestNavigatorPost(object):
    def test_post(self):
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
        router.post("/users", json={"name": "Thomas"}).mock(
            return_value=httpx.Response(
                200,
                headers={"Location": "http://test.com/users/thomas"},
                json=create_user("thomas", "Thomas").to_object(),
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

        result = navigator.post("users", {"name": "Thomas"})
        assert result.status() == 200
        assert result.get_header("Location") == "http://test.com/users/thomas"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
