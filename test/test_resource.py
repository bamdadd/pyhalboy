import unittest

from pyhalboy.pyhalboy import Resource


def createUser(id, name):
    return Resource() \
        .add_link('self', '/users/{}'.format(id)) \
        .add_property('name', name)


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

    def test_add_nil_link(self):
        resource = Resource().add_links({'ea:basket': None,
                                         "ea:customer": False,
                                         "self": "/order/123"})
        self.assertEqual({'_links': {'self': {'href': '/order/123'}}}, resource.to_object())

    def test_hrefs(self):
        resource = Resource().add_links({'ea:basket': '/baskets/123123',
                                         "ea:customer": '/customers/3474',
                                         "self": "/order/123"})
        self.assertEqual({'ea:basket': '/baskets/123123',
                          "ea:customer": '/customers/3474',
                          "self": "/order/123"}, resource.get_hrefs())

    def test_get_links(self):
        resource = Resource().add_links({'ea:basket': '/baskets/123123',
                                         "ea:customer": '/customers/3474',
                                         "self": "/order/123"})

        self.assertEqual({'ea:basket': {'href': '/baskets/123123'},
                          'ea:customer': {'href': '/customers/3474'},
                          'self': {'href': '/order/123'}}, resource.get_links())

    def test_add_resource(self):
        resource = Resource() \
            .add_resource('users', [createUser('fred', 'Fred'),
                                    createUser('sue', 'Sue'),
                                    createUser('mary', 'Mary'),
                                    ])
        self.assertEqual({'users': [{'_links': {'self': {'href': '/users/fred'}},
                                                   'name': 'Fred'},
                                                  {'_links': {'self': {'href': '/users/sue'}},
                                                   'name': 'Sue'},
                                                  {'_links': {'self': {'href': '/users/mary'}},
                                                   'name': 'Mary'}]}, resource.get_resources())

    def test_get_resources(self):
        resource1 = Resource().add_links(
            {
                'self': {'href': '/orders/124'},
                'ea:basket': {'href': '/baskets/98713'},
                'ea:customer': {'href': '/customers/12369'}
            })
        resource2 = Resource().add_links(
            {
                'self': {'href': '/orders/124'},
                'ea:basket': {'href': '/baskets/98713'},
                'ea:customer': {'href': '/customers/12369'}
            })

        resource = Resource() \
            .add_resource('ea:order', resource1) \
            .add_resource('ea:address', resource2)

        self.assertEqual({'ea:address': {'_links': {'ea:basket': {'href': '/baskets/98713'},
                                                    'ea:customer': {'href': '/customers/12369'},
                                                    'self': {'href': '/orders/124'}}},
                          'ea:order': {'_links': {'ea:basket': {'href': '/baskets/98713'},
                                                  'ea:customer': {'href': '/customers/12369'},
                                                  'self': {'href': '/orders/124'}}}}, resource.get_resources())

    def test_stack_resources(self):
        resource1 = Resource().add_links(
            {
                'self': {'href': '/orders/123'},
                'ea:basket': {'href': '/baskets/98712'},
                'ea:customer': {'href': '/customers/7809'}
            })
        resource2 = Resource().add_links(
            {
                'self': {'href': '/orders/124'},
                'ea:basket': {'href': '/baskets/98713'},
                'ea:customer': {'href': '/customers/12369'}
            })
        resource3 = Resource().add_links(
            {
                'self': {'href': '/orders/125'},
                'ea:basket': {'href': '/baskets/98716'},
                'ea:customer': {'href': '/customers/2416'}
            })

        resource = Resource() \
            .add_resource('ea:order', [resource1, resource2]) \
            .add_resource('ea:order', resource3)

        self.assertEqual([resource1,
                          resource2,
                          resource3], resource.get_resource("ea:order"))

    def test_add_property(self):
        resource = Resource().add_property('currentlyProcessing', 14)
        self.assertEqual(14, resource.get_property("currentlyProcessing"))

    def test_add_properties(self):
        resource = Resource().add_properties({'currentlyProcessing': 14,
                                              'state': 'processing'})
        self.assertEqual(14, resource.get_property("currentlyProcessing"))
        self.assertEqual('processing', resource.get_property("state"))

    def test_to_object(self):
        resource1 = Resource().add_links(
            {
                'self': {'href': '/orders/124'},
                'ea:basket': {'href': '/baskets/98713'},
                'ea:customer': {'href': '/customers/12369'}
            })

        resource = Resource() \
            .add_properties({'currentlyProcessing': 14,
                             'state': 'processing'}) \
            .add_links(
            {
                'self': {'href': '/orders/125'},
                'ea:basket': {'href': '/baskets/98716'},
                'ea:customer': {'href': '/customers/2416'}
            }).add_resource('ea:order', resource1)

        self.assertEqual({'_embedded':
                              {'ea:order':
                                   {'_links':
                                        {'ea:basket': {'href': '/baskets/98713'},
                                         'ea:customer': {'href': '/customers/12369'},
                                         'self': {'href': '/orders/124'}}}},
                          '_links':
                              {'ea:basket': {'href': '/baskets/98716'},
                               'ea:customer': {'href': '/customers/2416'},
                               'self': {'href': '/orders/125'}},
                          'currentlyProcessing': 14,
                          'state': 'processing'}, resource.to_object())

    # def test_obj_to_resource(self):
    #     resource = Resource().add_properties({'currentlyProcessing': 14,
    #                                           'state': 'processing'})
    #     obj = resource.to_object()
    #     obj_resource = object_to_resource(obj)
    #     self.assertEqual(obj_resource.get_property('currentlyProcessing'), 14)
    #     self.assertEqual(obj_resource.get_property('state'), 'processing')

    # def test_obj_to_resource_dict(self):
    #     obj = {'orders': [{'currentlyProcessing': 14, 'state': 'processing'}, {'currentlyProcessing': 14, 'state': 'processing'}]}
    #     obj_resource = object_to_resource(obj)
    #     self.assertEqual(obj_resource.get_property('currentlyProcessing'), 14)
    #     self.assertEqual(obj_resource.get_property('state'), 'processing')

    # def test_obj_to_resource2(self):
    #     resource1 = Resource().add_properties({'currentlyProcessing': 14,
    #                                            'state': 'processing'})
    #     resource2 = Resource().add_properties({'currentlyProcessing': 14,
    #                                            'state': 'processing'})
    #     resource = Resource() \
    #         .add_resource('orders', resource1) \
    #         .add_resource('orders', resource2)
    #     obj = resource.to_object()
    #     obj_resource = object_to_resource(obj['_embedded'])
    #     print(obj_resource.get_properties())
    #     self.assertEqual(obj_resource.get_property('currentlyProcessing'), 14)
    #     self.assertEqual(obj_resource.get_property('state'), 'processing')


if __name__ == '__main__':
    unittest.main()
