# Powerlibs: Django Restless Contrib

Contrib modules for Powerlibs Django Restless. 
 

## Usage

### PaginatedEndpointMixin

You must set `DEFAULT_PAGE_SIZE` on `settings.py`.


```python
from powerlibs.django.restless.endpoints import ListEndpoint
from powerlibs.django.restless.contrib.endpoints import PaginatedEndpointMixin

from .models import MyModel


class MyModelListEndpoint(PaginatedEndpointMixin, ListEndpoint):
    model = MyModel
```


Result:

```
GET http://localhost:8000/v1/my-model/
{
  "total": 100,
  "count": 10,
  "results": [{"id": 1, "name": "John Doe", ...}, ...]
}

GET http://localhost:8000/v1/my-model/?_limit=5
{
  "total": 100,
  "count": 5,
  "results": [{"id": 1, "name": "John Doe", ...}, ...]
}

GET http://localhost:8000/v1/my-model/?_limit=5&_offset=10
{
  "total": 100,
  "count": 5,
  "results": [{"id": 11, "name": "Mary Doe", ...}, ...]
}
```

### FilteredEndpointMixin:

```python
from powerlibs.django.restless.endpoints import ListEndpoint
from powerlibs.django.restless.contrib.endpoints import PaginatedEndpointMixin, FilteredEndpointMixin

from .models import MyModel


class MyModelListEndpoint(FilteredEndpointMixin, PaginatedEndpointMixin, ListEndpoint):
    model = MyModel
```


Result:

```
GET http://localhost:8000/v1/my-model/
{
  "total": 2,
  "count": 2,
  "results": [
    {"id": 1, "name": "John Doe"},
    {"id": 2, "name": "Mary Doe"},
  ]
}


GET http://localhost:8000/v1/my-model/?name=Mary Doe
{
  "total": 2,
  "count": 1,
  "results": [
    {"id": 2, "name": "Mary Doe"},
  ]
}


GET http://localhost:8000/v1/my-model/?id__lte=1
{
  "total": 2,
  "count": 2,
  "results": [
    {"id": 1, "name": "John Doe"},
  ]
}
```

### SoftDeletableListEndpointMixin

```python
from powerlibs.django.restless.endpoints import ListEndpoint
from powerlibs.django.restless.contrib.endpoints import PaginatedEndpointMixin, SoftDeletableListEndpointMixin

from .models import MyModel


class MyModelListEndpoint(SoftDeletableListEndpointMixin, PaginatedEndpointMixin, ListEndpoint):
    model = MyModel
```

Result:

Objects whose `deleted` field is `True` won't be shown into the list.


### SoftDeletableDetailEndpointMixin

```python
from powerlibs.django.restless.endpoints import DetailEndpoint
from powerlibs.django.restless.contrib.endpoints import PaginatedEndpointMixin, SoftDeletableDetailEndpointMixin

from .models import MyModel


class MyModelDetailEndpoint(SoftDeletableDetailEndpointMixin, DetailEndpoint):
    model = MyModel
```


Result:

`DELETE` verb will mark the object as `deleted=True`.

### JSONFieldDetailEndpointMixin

DjangoRestless, by itself, doesn't try to decode the value of Postgres
JSONField. This mixin turns the values of those fields into dicts so it is
normally encoded/decoded as JSON on the response.


```python
from powerlibs.django.restless.endpoints import DetailEndpoint
from powerlibs.django.restless.contrib.endpoints.json import JSONFieldDetailEndpointMixin

from .models import MyModel


class MyModelDetailEndpoint(JSONFieldDetailEndpointMixin, DetailEndpoint):
    model = MyModel
```


Result (in the example, `attributes` is a `JSONField`):

```
GET http://localhost:8000/v1/my-model/1
{
  "id": 1,
  "name": "John Doe",
  "attributes": {
    "favorite_music": ["jazz", "classical", "melodic death metal"]
  }
}
```


### JSONFieldListEndpointMixin

The same as JSONFieldDetailEndpointMixin, but for listing.

Also, you can POST the contents of the JSONField as JSON, not a JSON
serialized string.


### GeoJSONDetailEndpointMixin

Since PostGIS uses WKT to save geometries/features, this mixin adds the
same features but in GeoJSON. For example: is your model has a field named
`geom`, using this mixin your responses payloads will contain a `geom` key
with the WKT data and a `geom__geojson` key with the equivalent GeoJSON
data.


```python
from powerlibs.django.restless.endpoints import DetailEndpoint
from powerlibs.django.restless.contrib.endpoints.json import GeoJSONDetailEndpointMixin

from .models import MyModel


class MyModelDetailEndpoint(GeoJSONDetailEndpointMixin, DetailEndpoint):
    model = MyModel
```


Result:

```
GET http://localhost:8000/v1/my-model/1
{
  "id": 1,
  "geom": "POINT (1 1)",
  "geom__geojson": {
    'type': 'Point',
    'coordinates': [1, 1]
  }
}
```


### GeoJSONListEndpointMixin

The same thing, but for listing.

It also allows you to send only `geom__geojson` key and it will be saved
as the correspondent WKT.


### NestedEntitiesDetailEndpointMixin

You can use a query parameter `_nested` passing a comma-separated list of
field names of which you want to "nest" "sub-models", that is, ForeignKey
fields you want to expand with the actual objects, not only their IDs.

It was written trying to not mess with the basic format of a GET response
payload, so it adds a `_related` key in which the related objects are
included.


```python
from powerlibs.django.restless.endpoints import DetailEndpoint
from powerlibs.django.restless.contrib.endpoints.nested import NestedEntitiesDetailEndpointMixin

from .models import MyModel


class MyModelDetailEndpoint(NestedEntitiesDetailEndpointMixin, DetailEndpoint):
    model = MyModel
```


Result:

```
GET http://localhost:8000/v1/my-model/1?_nested=group,account_manager
{
  "id": 1,
  "name": "John Doe",
  "group": 1,
  "account_manager": 2,
  "_related": {
    "group": {
      "id": 1,
      "name": "Regular clients",
    },
    "account_manager": {
      "id": 2,
      "name": "Suzy Silva",
    }
  }
}
```


### NestedEntitiesListEndpointMixin

The same thing, but for listing.

It is not very optimized and **will** make at least one new database hit
per item on list, so avoid, for now, using it on lengthy listings.
