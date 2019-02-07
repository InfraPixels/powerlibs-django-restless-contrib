import json

from powerlibs.django.restless.http import JSONResponse


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
        return self.hydrate_data_json(super().get(request, *args, **kwargs))

    def patch(self, request, *args, **kwargs):
        # We don't need to "treat" sent data, since
        # the PATCH method is implemented without any
        # serialization involved.
        return self.hydrate_data_json(super().patch(request, *args, **kwargs))

    def put(self, request, *args, **kwargs):
        self.treat_sent_data(request)
        return self.hydrate_data_json(super().put(request, *args, **kwargs))

    def do_hydrate_data_json(self, serialized_data):
        for field_name, field_type in self.get_json_fields_and_types():
            serialized_data[field_name] = eval(serialized_data[field_name])

    def hydrate_data_json(self, response):
        if isinstance(response, JSONResponse):
            serialized_data = json.loads(response.content)
            self.do_hydrate_data_json(serialized_data)
            response.content = json.dumps(serialized_data)
        elif isinstance(response, dict):
            self.do_hydrate_data_json(response)

        return response


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

        if isinstance(serialized_objects, (list, tuple)):
            for obj in serialized_objects:
                generate_json(obj)
        else:
            generate_json(serialized_objects)

        return serialized_objects

    def post(self, request, *args, **kwargs):
        self.treat_sent_data(request)
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        for field_name, field_type in self.get_json_fields_and_types():
            for param_name in request.GET.keys():
                part1 = param_name.split('__')[0]
                if part1 == field_name:
                    break
            else:
                continue

            value = request.GET.get(param_name, None)
            if value and value.startswith('[') and value.endswith(']'):
                request.GET._mutable = True
                values = value[1:-1].split(',')

                try:
                    integer_values = [int(x) for x in values]
                except:
                    request.GET[param_name] = values
                else:
                    request.GET[param_name] = integer_values

                request.GET._mutable = False

        return super().get(request, *args, **kwargs)
