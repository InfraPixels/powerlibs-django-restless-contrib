from unittest import mock


def test_nested_detail_endpoint_mixin(nested_detail_endpoint):
    mocked_request = mock.Mock(GET={'_nested': 'related_model'})

    response = nested_detail_endpoint.get(mocked_request)

    assert '_related' in response
