import unittest

from resource import Resource


class ResourceTestCase(unittest.TestCase):

    def test_add_link(self):
        resource = Resource().add_link('self', {'href': '/orders'})
        self.assertEqual(resource.get_link('self'), {'href': '/orders'})

    def test_add_link_string(self):
        resource = Resource().add_link('self', '/orders')
        self.assertEqual(resource.get_link('self'), {'href': '/orders'})

    def test_add_link_stacking_keys(self):
        resource = Resource() \
            .add_link('ea:admin', {'href': '/admins/2', 'title': 'Fred'}) \
            .add_link('ea:admin', {'href': '/admins/5', 'title': 'Kate'})

        self.assertEqual([
            {'href': '/admins/2', 'title': 'Fred'},
            {'href': '/admins/5', 'title': 'Kate'}
        ], resource.get_link('ea:admin'))

    def test_add_links(self):
        resource = Resource().add_links({'self': {'href': '/orders'},
                                         'ea:basket': {'href': '/baskets/123123'},
                                         'ea:customer': {'href': '/customers/3474'}})

        self.assertEqual(resource.get_href('ea:basket'), '/baskets/123123')
        self.assertEqual(resource.get_href('ea:customer'), '/customers/3474')

    def test_add_non_link(self):
        resource = Resource().add_link('ea:basket', None)
        self.assertEqual({}, resource.to_object())


if __name__ == '__main__':
    unittest.main()
