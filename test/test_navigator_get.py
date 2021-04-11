import unittest
import requests_mock

from pyhalboy.resource import Resource
from pyhalboy.navigator import Navigator


def createUser(id, name):
    return Resource() \
        .add_link('self', '/users/{}'.format(id)) \
        .add_property('name', name) \
        .add_property('id', id)


class NavigatorGetTestCase(unittest.TestCase):
    def test_get(self):
        with requests_mock.Mocker() as m:
            m.get('http://test.com', json={"_links":
                                               {"users": {"href": "/users"}},
                                           "_embedded": {},
                                           "prop1": 1})
            m.get('http://test.com/users',
                  json=Resource() \
                  .add_property('test', 1)
                  .add_link('self', 'http://test.com/users')
                  .add_resource('users', [createUser('fred', 'Fred'),
                                          createUser('sue', 'Sue'),
                                          createUser('mary', 'Mary'),
                                          ])
                  .to_object())
            navigator = Navigator()
            headers = {
                "authorization": 'some-token'
            }
            discovery_result = navigator.discover('http://test.com', {"http": {"headers": headers}})
            result = discovery_result.get('users')
            self.assertEqual(result.status(), 200)

            users = result.resource().get_resource('users')
            names = list(map(lambda u: u.get_property('name'), users))

            self.assertEqual(result.resource().get_property('test'), 1)
            self.assertEqual(result.resource().get_href('self'), 'http://test.com/users')
            self.assertEqual(names, ['Fred', 'Sue', 'Mary'])

    def test_get_with_params(self):
        with requests_mock.Mocker() as m:
            m.get('http://test.com', json={"_links":
                                               {"user":
                                                    {"href": "/users/{userId}",
                                                     "templated": True}},
                                           })
            m.get('http://test.com/users/fred',
                  json=createUser('fred', 'Fred')
                  .to_object())
            navigator = Navigator()
            discovery_result = navigator.discover('http://test.com',)
            result = discovery_result.get('user', {"userId": "fred"})
            self.assertEqual(result.status(), 200)

            self.assertEqual(result.resource().get_property('name'), 'Fred')


if __name__ == '__main__':
    unittest.main()
