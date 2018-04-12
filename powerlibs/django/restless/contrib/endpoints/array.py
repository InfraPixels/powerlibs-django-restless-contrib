import json

from powerlibs.django.restless.http import JSONResponse


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
                request.data[field_name] = ','.join(str(v) for v in value)

    def _treat_sent_data_for_patch(self, request):
        for field_name, _ in self.get_array_fields_and_types():
            try:
                value = request.data[field_name]
            except KeyError:
                continue

            if value is not None:
                core = ','.join(str(v) for v in value)
                request.data[field_name] = '{' + core + '}'


class ArrayFieldDetailEndpointMixin(ArrayFieldsEndpoint):
    def get(self, request, *args, **kwargs):
        return self.hydrate_data_arrayfield(super().get(request, *args, **kwargs))

    def patch(self, request, *args, **kwargs):
        self._treat_sent_data_for_patch(request)
        return self.hydrate_data_arrayfield(super().patch(request, *args, **kwargs))

    def put(self, request, *args, **kwargs):
        self._treat_sent_data(request)
        return self.hydrate_data_arrayfield(super().put(request, *args, **kwargs))

    def do_hydrate_data_arrayfield(self, serialized_data):
        for field_name, _ in self.get_array_fields_and_types():
            if field_name in serialized_data:
                value = serialized_data[field_name]
                if isinstance(value, str):
                    if value.startswith('{') and value.endswith('}'):
                        serialized_data[field_name] = value[1:-1].split(',')
                    else:
                        serialized_data[field_name] = eval(value)

    def hydrate_data_arrayfield(self, response):
        if isinstance(response, JSONResponse):
            serialized_data = json.loads(response.content)
            self.do_hydrate_data_arrayfield(serialized_data)
            response.content = json.dumps(serialized_data)
        elif isinstance(response, dict):
            self.do_hydrate_data_arrayfield(response)
        return response


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
