class ArrayFieldsEndpoint():
    def get_array_fields_and_types(self):
        for field in self.model._meta.fields:
            class_name = field.__class__.__name__
            if class_name in ('ArrayField',):
                yield (field.name, class_name)

    def _treat_sent_data(self, request):
        for field_name, _ in self.get_array_fields_and_types():
            try:
                value = request.data[field_name]
            except KeyError:
                continue

            if value is not None:
                request.data[field_name] = ','.join(str(value))


class ArrayFieldDetailEndpointMixin(ArrayFieldsEndpoint):
    def get(self, request, *args, **kwargs):
        serialized_data = super().get(request, *args, **kwargs)

        for field_name, field_type in self.get_array_fields_and_types():
            serialized_data[field_name] = eval(serialized_data[field_name])

        return serialized_data

    def patch(self, request, *args, **kwargs):
        self._treat_sent_data(request)
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        self._treat_sent_data(request)
        return super().put(request, *args, **kwargs)


class ArrayFieldListEndpointMixin(ArrayFieldsEndpoint):
    def serialize(self, objects):
        serialized_objects = super().serialize(objects)
        fields_data = [(field_name, field_type) for field_name, field_type in self.get_array_fields_and_types()]

        def generate_array(obj):
            for field_name, field_type in fields_data:
                value = obj[field_name]
                if value:
                    # DjangoRestless makes a str(list), so we can safely use a `eval`, here:
                    obj[field_name] = eval(value)

        if type(serialized_objects) in (list, tuple):
            for obj in serialized_objects:
                generate_array(obj)
        else:
            generate_array(serialized_objects)

        return serialized_objects

    def post(self, request, *args, **kwargs):
        self._treat_sent_data(request)
        return super().post(request, *args, **kwargs)
