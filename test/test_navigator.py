import sys
import pytest

import httpx
import respx

from pyhalboy.navigator import Navigator


class TestNavigatorTestCase(object):
    def test_discover(self):
        router = respx.Router()
        router.get("http://test.com").mock(
            return_value=httpx.Response(
                200,
                json={
                    "_links": {"users": {"href": "/users"}},
                    "_embedded": {},
                    "prop1": 1,
                },
            )
        )
        client = httpx.Client(
            transport=httpx.MockTransport(handler=router.handler)
        )

        headers = {"authorization": "some-token"}
        navigator = Navigator.discover(
            "http://test.com",
            settings={"client": client, "http": {"headers": headers}},
        )

        assert navigator.status() == 200

        href = navigator.resource().get_href("users")
        assert href == "/users"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
