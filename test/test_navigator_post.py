import sys
import pytest

import requests_mock

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
        with requests_mock.Mocker() as m:
            m.get(
                "http://test.com",
                json={
                    "_links": {"users": {"href": "/users"}},
                    "_embedded": {},
                    "prop1": 1,
                },
            )

            m.post(
                "http://test.com/users",
                json={"name": "Thomas"},
                headers={"Location": "http://test.com/users/thomas"},
            )
            navigator = Navigator()
            headers = {"authorization": "some-token"}
            discovery_result = navigator.discover(
                "http://test.com", {"http": {"headers": headers}}
            )
            result = discovery_result.post("users", {"name": "Thomas"})
            assert result.status() == 200
            assert (
                result.get_header("Location") == "http://test.com/users/thomas"
            )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
