from unittest import mock


def test_paginated_endpoint_mixin(paginated_endpoint):
    mocked_request = mock.Mock(GET={'_limit': 2, '_offset': 1})

    response = paginated_endpoint.get(mocked_request)

    assert response['total'] == 5
    assert response['count'] == 2

    assert response['results'][0].id == 2
    assert response['results'][1].id == 3


def test_filtered_endpoint_mixin(filtered_endpoint):
    get_parameters = {
        'id': 1, 'nonexistent_field': 'MUST NOT BE SHOWN',
        '_limit': 1, '_nonexistent_key': 999
    }

    mocked_request = mock.Mock(GET=get_parameters)

    queryset = filtered_endpoint.get_query_set(mocked_request)

    assert len(queryset) == 1
    assert queryset.count() == 1
    assert queryset[0].id == get_parameters['id']


def test_filtered_endpoint_mixin_model_fields_property(original_filtered_endpoint):
    fields = original_filtered_endpoint.model_fields
    assert len(fields) == 2
    assert fields[0] == 'id'
    assert fields[1] == 'name'


def test_soft_deletable_detail_endpoint_mixin(soft_deletable_detail_endpoint):
    soft_deletable_detail_endpoint.delete(None)
    assert soft_deletable_detail_endpoint.instance.deleted is True


def test_soft_deletable_detail_endpoint_mixin_on_already_deleted_instance(soft_deletable_detail_endpoint_with_deleted_instance):
    soft_deletable_detail_endpoint_with_deleted_instance.delete(None)
    assert soft_deletable_detail_endpoint_with_deleted_instance.instance.deleted is True


def test_soft_deletable_list_endpoint(soft_deletable_list_endpoint):
    qs = soft_deletable_list_endpoint.get_query_set(None)
    assert len(qs) == 3
    assert qs.count() == 3
    assert qs[0].deleted is False
    assert qs[1].deleted is False
    assert qs[2].deleted is False
