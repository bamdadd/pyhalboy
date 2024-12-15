import sys
import pytest

import requests_mock

from pyhalboy.navigator import Navigator


class TestNavigatorTestCase(object):
    def test_discover(self):
        with requests_mock.Mocker() as m:
            m.get(
                "http://test.com",
                json={
                    "_links": {"users": {"href": "/users"}},
                    "_embedded": {},
                    "prop1": 1,
                },
            )
            navigator = Navigator()
            headers = {"authorization": "some-token"}
            discovery_result = navigator.discover(
                "http://test.com", {"http": {"headers": headers}}
            )
            assert discovery_result.status() == 200

            href = discovery_result.resource().get_href("users")
            assert href == "/users"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
