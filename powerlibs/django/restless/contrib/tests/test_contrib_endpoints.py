from unittest import mock

from powerlibs.django.results.contrib.endpoints import PaginatedEndpointMixin, FilteredEndpointMixin, SoftDeletableEndpointMixin


def test_paginated_endpoint_mixin():
    class MyQuerySet(list):
        def count(self):
            return len(self)

        def __getitem__(self, slice):
            results = super().__getitem__(slice)
            return MyQuerySet(results)

    mocked_queryset = MyQuerySet([1, 2, 3, 4, 5])

    class MyClass(PaginatedEndpointMixin):
        get_query_set = mock.Mock(return_value=mocked_queryset)

        def serialize(self, arg):
            return arg

    mocked_request = mock.Mock(GET={'_limit': 2, '_offset': 1})

    obj = MyClass()
    response = obj.get(mocked_request)

    assert response['total'] == 5
    assert response['count'] == 2
    assert response['results'] == [2, 3]


def test_filtered_endpoint_mixin():
    class MyQuerySet(list):
        def filter(self, **kwargs):
            return "FILTERED QUERYSET: {}".format(kwargs)

    mocked_queryset = MyQuerySet([1, 2, 3, 4, 5])

    class ParentClass:
        get_query_set = mock.Mock(return_value=mocked_queryset)

    class MyClass(FilteredEndpointMixin, ParentClass):
        model_fields = ('id', 'username', 'email')

    filter_parameters = {'id': 1, 'nonexistent_field': 'MUST NOT BE SHOWN'}
    get_parameters = {'_limit': 1, '_nonexistent_key': 999}
    get_parameters.update(filter_parameters)

    mocked_request = mock.Mock(GET=get_parameters)

    obj = MyClass()
    queryset = obj.get_query_set(mocked_request)

    assert queryset == "FILTERED QUERYSET: {'id': 1}"


def test_soft_deletable_endpoint_mixin():
    instance = mock.Mock(deleted=False)

    class MyClass(SoftDeletableEndpointMixin):
        get_instance = mock.Mock(return_value=instance)

    obj = MyClass()
    obj.delete(None)

    assert instance.deleted is True


def test_soft_deletable_endpoint_mixin_on_already_deleted_instance():
    instance = mock.Mock(deleted=True)

    class MyClass(SoftDeletableEndpointMixin):
        get_instance = mock.Mock(return_value=instance)

    obj = MyClass()
    obj.delete(None)

    assert instance.deleted is True
