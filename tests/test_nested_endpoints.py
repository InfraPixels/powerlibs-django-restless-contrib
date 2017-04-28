from unittest import mock


def test_nested_detail_endpoint_mixin(nested_detail_endpoint):
    mocked_request = mock.Mock(GET={'_nested': 'related_model'})

    response = nested_detail_endpoint.get(mocked_request)

    assert '_related' in response


def test_nested_list_endpoint_mixin(nested_list_endpoint):
    mocked_request = mock.Mock(GET={'_nested': 'related_model'})

    response = nested_list_endpoint.get(mocked_request)

    assert '_related' in response[0]
