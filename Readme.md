# PyHalboy


A library for all things hypermedia. insipred by [Halboy](https://github.com/jimmythompson/halboy/) and [Halboy.js](https://github.com/jimmythompson/halboy.js/)

* Create hypermedia resources
* Marshal to and from plain JS objects
* Navigate JSON+HAL APIs

## API

### Resources

With PyHalboy you can create resources, and pull information from them.

```python
from 'pyhalboy' import Resource

discountResource = Resource()
    .add_link('self', '/discounts/1256')
    .add_property('discountPercentage', 10)

itemResources = [
   Resource()
    .add_link('self', '/items/534')
    .add_property('price', 25.48)
]

resource = Resource()
      .add_link('self', '/orders/123')
      .add_link('creator', '/users/rob')
      .add_resource('discount', discountResource)
      .add_resource('items', itemResources)
      .add_property('state', 'dispatching')

resource.get_link('self')
// { href: '/orders/123' }

resource.get_href('self')
// '/orders/123'

resource.get_property('state')
// 'dispatching'

resource
  .get_resource('creator')
  .get_property('discountPercentage')
// 10

resource
  .get_resource('items')[0]
  .get_property('price')
// 25.48
```

### Marshalling

You can create HAL resources from plain JS objects, and vice versa.

```python
from 'pyhalboy' import Resource

itemResources = [
   Resource()
    .add_link('self', '/items/534')
    .add_property('price', 25.48)
]

resource =
    new Resource()
      .add_link('self', '/orders/123')
      .add_link('creator', '/users/rob')
      .add_resource('items', itemResources)
      .add_property('state', 'dispatching')

resource.to_object()
// {
//   _links: {
//     self: { href: '/orders/123' },
//     creator: { href: '/users/rob' }
//   },
//   _embedded: {
//     items: [{
//       _links: {
//         self: { href: '/items/534' }
//       },
//       price: 25.48
//     }]
//   },
//   state: 'dispatching'
// }

Resource.fromObject(resource.to_object())
  .get_href('self')
// '/orders/123'
```

### Navigation

Provided you're calling a HAL+JSON API, you can discover the API and navigate
through its links. When you've found what you want, you call
`navigator.resource()` and you get a plain old HAL resource, which you can inspect
using any of the methods above.

```python
from 'pyhalboy' import Navigator

//  GET / - 200 OK
//  {
//   "_links": {
//     "self": {
//       "href": "/"
//     },
//     "users": {
//       "href": "/users"
//     },
//     "user": {
//       "href": "/users/{id}",
//       "templated": true
//     }
//   }
// }

discovery_result = Navigator.discover('https://api.example.com/')
users_result =  discovery_result.get('users')

users_result.status()
// 200

users_result.location()
// 'https://api.example.com/users'

robResult =  discovery_result.get('user', {id :'rob'})

robResult.location()
// 'https://api.example.com/users/rob'

sue_result =  discovery_result.post('user', {
  'id': 'sue',
  'name': 'Sue',
  'title': 'Dev'
})

sue_result.location()
// 'https://api.example.com/users/sue'

sue_result
  .resource()
  .get_property('title')
// 'Dev'
```