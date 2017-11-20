import json
from unittest import mock


def test_json_field_detail_endpoint_mixin(json_field_detail_endpoint):
    mocked_request = mock.Mock(GET={'_JSON': 'related_model'})

    response = json_field_detail_endpoint.get(mocked_request)

    assert json.dumps(response)


def test_json_field_list_endpoint_mixin(json_field_list_endpoint):
    mocked_objects = mock.Mock('objects')

    response = json_field_list_endpoint.serialize(mocked_objects)

    assert json.dumps(response)
