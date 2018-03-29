import json


class JSONFieldsEndpoint():
    def get_json_fields_and_types(self):
        for field in self.model._meta.fields:
            class_name = field.__class__.__name__
            if class_name in ('HStoreField', 'JSONField'):
                yield (field.name, class_name)

    def treat_sent_data(self, request):
        for field_name, _ in self.get_json_fields_and_types():
            try:
                value = request.data[field_name]
            except KeyError:
                continue

            if value is not None:
                request.data[field_name] = json.dumps(value)


class JSONFieldDetailEndpointMixin(JSONFieldsEndpoint):
    def get(self, request, *args, **kwargs):
        serialized_data = super().get(request, *args, **kwargs)

        for field_name, field_type in self.get_json_fields_and_types():
            serialized_data[field_name] = eval(serialized_data[field_name])

        return serialized_data

    def patch(self, request, *args, **kwargs):
        # We don't need to "treat" sent data, since
        # the PATCH method is implemented without any
        # serialization involved.
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        self.treat_sent_data(request)
        return super().put(request, *args, **kwargs)


class JSONFieldListEndpointMixin(JSONFieldsEndpoint):
    def serialize(self, objects):
        serialized_objects = super().serialize(objects)
        fields_data = [(field_name, field_type) for field_name, field_type in self.get_json_fields_and_types()]

        def generate_json(obj):
            for field_name, field_type in fields_data:
                value = obj[field_name]
                if value:
                    if isinstance(value, dict):
                        obj[field_name] = value
                    else:
                        # DjangoRestless makes a str(dict), so we can safely use a `eval`, here:
                        obj[field_name] = eval(value)

        if type(serialized_objects) in (list, tuple):
            for obj in serialized_objects:
                generate_json(obj)
        else:
            generate_json(serialized_objects)

        return serialized_objects

    def post(self, request, *args, **kwargs):
        self.treat_sent_data(request)
        return super().post(request, *args, **kwargs)
