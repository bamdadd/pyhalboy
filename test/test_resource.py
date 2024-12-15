import sys
import pytest

from pyhalboy import Resource


def create_user(id, name):
    return (
        Resource()
        .add_link("self", "/users/{}".format(id))
        .add_property("name", name)
    )


class TestResource(object):
    def test_add_link(self):
        resource = Resource().add_link("self", {"href": "/orders"})
        assert resource.get_link("self") == {"href": "/orders"}

    def test_add_link_string(self):
        resource = Resource().add_link("self", "/orders")
        assert resource.get_link("self") == {"href": "/orders"}

    def test_add_link_stacking_keys(self):
        resource = (
            Resource()
            .add_link("ea:admin", {"href": "/admins/2", "title": "Fred"})
            .add_link("ea:admin", {"href": "/admins/5", "title": "Kate"})
        )

        assert resource.get_link("ea:admin") == [
            {"href": "/admins/2", "title": "Fred"},
            {"href": "/admins/5", "title": "Kate"},
        ]

    def test_add_links(self):
        resource = Resource().add_links(
            {
                "self": {"href": "/orders"},
                "ea:basket": {"href": "/baskets/123123"},
                "ea:customer": {"href": "/customers/3474"},
            }
        )

        assert resource.get_href("ea:basket") == "/baskets/123123"
        assert resource.get_href("ea:customer") == "/customers/3474"

    def test_add_non_link(self):
        resource = Resource().add_link("ea:basket", None)

        assert resource.to_object() == {}

    def test_add_nil_link(self):
        resource = Resource().add_links(
            {"ea:basket": None, "ea:customer": False, "self": "/order/123"}
        )

        assert resource.to_object() == {
            "_links": {"self": {"href": "/order/123"}}
        }

    def test_hrefs(self):
        resource = Resource().add_links(
            {
                "ea:basket": "/baskets/123123",
                "ea:customer": "/customers/3474",
                "self": "/order/123",
            }
        )

        assert resource.get_hrefs() == {
            "ea:basket": "/baskets/123123",
            "ea:customer": "/customers/3474",
            "self": "/order/123",
        }

    def test_multiple_hrefs(self):
        resource = (
            Resource()
            .add_links(
                {
                    "ea:basket": "/baskets/123123",
                    "ea:customer": "/customers/3474",
                    "self": "/order/123",
                }
            )
            .add_link("ea:customer", "/customers/4567")
        )

        assert resource.get_hrefs() == {
            "ea:basket": "/baskets/123123",
            "ea:customer": ["/customers/3474", "/customers/4567"],
            "self": "/order/123",
        }

    def test_get_links(self):
        resource = Resource().add_links(
            {
                "ea:basket": "/baskets/123123",
                "ea:customer": "/customers/3474",
                "self": "/order/123",
            }
        )

        assert resource.get_links() == {
            "ea:basket": {"href": "/baskets/123123"},
            "ea:customer": {"href": "/customers/3474"},
            "self": {"href": "/order/123"},
        }

    def test_add_resource(self):
        resource = Resource().add_resource(
            "users",
            [
                create_user("fred", "Fred"),
                create_user("sue", "Sue"),
                create_user("mary", "Mary"),
            ],
        )

        assert resource.get_resources() == {
            "users": [
                {
                    "_links": {"self": {"href": "/users/fred"}},
                    "name": "Fred",
                },
                {
                    "_links": {"self": {"href": "/users/sue"}},
                    "name": "Sue",
                },
                {
                    "_links": {"self": {"href": "/users/mary"}},
                    "name": "Mary",
                },
            ]
        }

    def test_get_resources(self):
        resource1 = Resource().add_links(
            {
                "self": {"href": "/orders/124"},
                "ea:basket": {"href": "/baskets/98713"},
                "ea:customer": {"href": "/customers/12369"},
            }
        )
        resource2 = Resource().add_links(
            {
                "self": {"href": "/orders/124"},
                "ea:basket": {"href": "/baskets/98713"},
                "ea:customer": {"href": "/customers/12369"},
            }
        )

        resource = (
            Resource()
            .add_resource("ea:order", resource1)
            .add_resource("ea:address", resource2)
        )

        assert resource.get_resources() == {
            "ea:address": {
                "_links": {
                    "ea:basket": {"href": "/baskets/98713"},
                    "ea:customer": {"href": "/customers/12369"},
                    "self": {"href": "/orders/124"},
                }
            },
            "ea:order": {
                "_links": {
                    "ea:basket": {"href": "/baskets/98713"},
                    "ea:customer": {"href": "/customers/12369"},
                    "self": {"href": "/orders/124"},
                }
            },
        }

    def test_stack_resources(self):
        resource1 = Resource().add_links(
            {
                "self": {"href": "/orders/123"},
                "ea:basket": {"href": "/baskets/98712"},
                "ea:customer": {"href": "/customers/7809"},
            }
        )
        resource2 = Resource().add_links(
            {
                "self": {"href": "/orders/124"},
                "ea:basket": {"href": "/baskets/98713"},
                "ea:customer": {"href": "/customers/12369"},
            }
        )
        resource3 = Resource().add_links(
            {
                "self": {"href": "/orders/125"},
                "ea:basket": {"href": "/baskets/98716"},
                "ea:customer": {"href": "/customers/2416"},
            }
        )

        resource = (
            Resource()
            .add_resource("ea:order", [resource1, resource2])
            .add_resource("ea:order", resource3)
        )

        assert resource.get_resource("ea:order") == [
            resource1,
            resource2,
            resource3,
        ]

    def test_add_property(self):
        resource = Resource().add_property("currentlyProcessing", 14)

        assert resource.get_property("currentlyProcessing") == 14

    def test_add_properties(self):
        resource = Resource().add_properties(
            {"currentlyProcessing": 14, "state": "processing"}
        )

        assert resource.get_property("currentlyProcessing") == 14
        assert resource.get_property("state") == "processing"

    def test_to_object(self):
        resource1 = Resource().add_links(
            {
                "self": {"href": "/orders/124"},
                "ea:basket": {"href": "/baskets/98713"},
                "ea:customer": {"href": "/customers/12369"},
            }
        )

        resource = (
            Resource()
            .add_properties({"currentlyProcessing": 14, "state": "processing"})
            .add_links(
                {
                    "self": {"href": "/orders/125"},
                    "ea:basket": {"href": "/baskets/98716"},
                    "ea:customer": {"href": "/customers/2416"},
                }
            )
            .add_resource("ea:order", resource1)
        )

        assert resource.to_object() == {
            "_embedded": {
                "ea:order": {
                    "_links": {
                        "ea:basket": {"href": "/baskets/98713"},
                        "ea:customer": {"href": "/customers/12369"},
                        "self": {"href": "/orders/124"},
                    }
                }
            },
            "_links": {
                "ea:basket": {"href": "/baskets/98716"},
                "ea:customer": {"href": "/customers/2416"},
                "self": {"href": "/orders/125"},
            },
            "currentlyProcessing": 14,
            "state": "processing",
        }

    # def test_obj_to_resource(self):
    #     resource = (
    #         Resource()
    #         .add_properties({
    #             'currentlyProcessing': 14,
    #                                           'state': 'processing'
    #         })
    #     )
    #
    #     obj = resource.to_object()
    #     obj_resource = object_to_resource(obj)
    #
    #     assert obj_resource.get_property('currentlyProcessing') == 14
    #     assert obj_resource.get_property('state') == 'processing'

    # def test_obj_to_resource_dict(self):
    #     obj = {
    #         'orders': [
    #             {'currentlyProcessing': 14, 'state': 'processing'},
    #             {'currentlyProcessing': 14, 'state': 'processing'}
    #         ]
    #     }
    #
    #     obj_resource = object_to_resource(obj)
    #
    #     assert obj_resource.get_property('currentlyProcessing') == 14
    #     assert obj_resource.get_property('state') == 'processing'

    # def test_obj_to_resource2(self):
    #     resource1 = (
    #         Resource()
    #         .add_properties({
    #             'currentlyProcessing': 14,
    #             'state': 'processing'
    #         })
    #     )
    #     resource2 = (
    #         Resource()
    #         .add_properties({
    #             'currentlyProcessing': 14,
    #             'state': 'processing'
    #         })
    #     )
    #     resource = (
    #         Resource()
    #         .add_resource('orders', resource1)
    #         .add_resource('orders', resource2)
    #     )
    #
    #     obj = resource.to_object()
    #     obj_resource = object_to_resource(obj['_embedded'])
    #
    #     print(obj_resource.get_properties())
    #
    #     assert obj_resource.get_property('currentlyProcessing') == 14
    #     assert obj_resource.get_property('state') == 'processing'


if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
