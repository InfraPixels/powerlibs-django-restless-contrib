import pytest
from unittest import mock

from powerlibs.django.restless.contrib.endpoints import PaginatedEndpointMixin, FilteredEndpointMixin, SoftDeletableDetailEndpointMixin, SoftDeletableListEndpointMixin


class MockedQuerySet(list):
    def count(self):
        return len(self)

    def __getitem__(self, slice):
        results = super().__getitem__(slice)
        if isinstance(results, list):
            return MockedQuerySet(results)
        else:
            return results

    def filter(self, **kwargs):
        results = []
        for item in self:
            for key, expected_value in kwargs.items():
                value = getattr(item, key)
                if value == expected_value:
                    results.append(item)

        return MockedQuerySet(results)


@pytest.fixture
def instances():
    return (
        mock.Mock(id=1, deleted=False),
        mock.Mock(id=2, deleted=False),
        mock.Mock(id=3, deleted=False),
        mock.Mock(id=4, deleted=True),
        mock.Mock(id=5, deleted=True),
    )


@pytest.fixture
def mocked_queryset(instances):
    return MockedQuerySet(instances)


class Endpoint:
    get_query_set = mock.Mock(return_value=mocked_queryset(instances()))


@pytest.fixture
def filtered_endpoint():
    class MyClass(FilteredEndpointMixin, Endpoint):
        model_fields = ('id', 'username', 'email')

    return MyClass()


@pytest.fixture
def original_filtered_endpoint():
    field_1 = mock.Mock()
    field_1.configure_mock(name='id')
    field_2 = mock.Mock()
    field_2.configure_mock(name='name')

    class MyClass(FilteredEndpointMixin, Endpoint):
        model = mock.Mock(
            _meta=mock.Mock(
                fields=(field_1, field_2)
            )
        )

    return MyClass()


@pytest.fixture
def paginated_endpoint():
    class MyClass(PaginatedEndpointMixin, Endpoint):
        def serialize(self, arg):
            return arg

    return MyClass()


@pytest.fixture
def soft_deletable_detail_endpoint():
    instance = mock.Mock(deleted=False)

    class MyClass(SoftDeletableDetailEndpointMixin):
        get_instance = mock.Mock(return_value=instance)

    obj = MyClass()
    obj.instance = instance
    return obj


@pytest.fixture
def soft_deletable_detail_endpoint_with_deleted_instance():
    instance = mock.Mock(deleted=True)

    class MyClass(SoftDeletableDetailEndpointMixin):
        get_instance = mock.Mock(return_value=instance)

    obj = MyClass()
    obj.instance = instance
    return obj


@pytest.fixture
def soft_deletable_list_endpoint():
    class MyClass(SoftDeletableListEndpointMixin, Endpoint):
        pass

    obj = MyClass()
    return obj
