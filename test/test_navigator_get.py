import unittest
import requests_mock

from pyhalboy.pyhalboy import Resource
from pyhalboy.pyhalboy import Navigator



def createUser(id, name):
    return Resource() \
        .add_link('self', '/users/{}'.format(id)) \
        .add_property('name', name)


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
                  # .add_resource('users', [createUser('fred', 'Fred'),
                  #                         createUser('sue', 'Sue'),
                  #                         createUser('mary', 'Mary'),
                  #                         ])
                  .to_object())
            navigator = Navigator()
            headers = {
                "authorization": 'some-token'
            }
            discovery_result = navigator.discover('http://test.com', {"http": {"headers": headers}})
            result = discovery_result.get('users')
            self.assertEqual(result.status(), 200)

            # users = result.resource().get_property('users')
            # print(users)
            # names = list(map(lambda u: u.get_property('name'), users))

            self.assertEqual(result.resource().get_property('test'), 1)
            self.assertEqual(result.resource().get_href('self'), 'http://test.com/users')


if __name__ == '__main__':
    unittest.main()
