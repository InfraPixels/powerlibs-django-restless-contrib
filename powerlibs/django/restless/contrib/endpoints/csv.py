import csv
from io import StringIO
import json

from django.http import HttpResponse

from powerlibs.django.restless.http import JSONResponse


class CSVListEndpointMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._csv_fieldnames = None

    def get_json_fields(self):
        for field in self.model._meta.fields:
            class_name = field.__class__.__name__
            if class_name in ('JSONField'):
                yield field.name

    def get_json_fieldnames(self, entries):
        json_fields = list(self.get_json_fields())
        json_keys = set()
        for json_field in json_fields:
            for entry in entries:
                value = entry[json_field]
                if isinstance(value, dict):
                    for key in value.keys():
                        key_name = f'{json_field}.{key}'
                        json_keys.add(key_name)
        return json_keys

    def hydrate_results_with_json_fields(self, results):
        json_fields = list(self.get_json_fields())
        for json_field in json_fields:
            for entry in results:
                value = entry[json_field]
                if isinstance(value, dict):
                    for key in value.keys():
                        key_name = f'{json_field}.{key}'
                        entry[key_name] = entry[json_field][key]

    def get_csv_fieldnames(self, entries):
        if self._csv_fieldnames is None:
            value = entries[0]
            if isinstance(value, dict):
                self._csv_fieldnames = list(key for key in entries[0].keys())
            else:
                self._csv_fieldnames = []
            self._csv_fieldnames.extend(self.get_json_fieldnames(entries))

        return self._csv_fieldnames

    def to_csv(self, results):
        if len(results) == 0:
            return ''

        fieldnames = self.get_csv_fieldnames(results)
        self.hydrate_results_with_json_fields(results)
        the_buffer = StringIO()

        csv_writer = csv.DictWriter(the_buffer, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(results)

        the_buffer.seek(0)
        body = the_buffer.read()
        return HttpResponse(body, content_type='text/csv')

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        accept = request.META.get('HTTP_ACCEPT', None)
        if accept is not None and 'text/csv' in accept:

            if isinstance(response, JSONResponse):
                serialized_data = json.loads(response.content)
                if 'results' in serialized_data:
                    csv_data = self.to_csv(serialized_data['results'])
                else:
                    csv_data = self.to_csv(serialized_data)

                response.content = json.dumps(csv_data)

            elif isinstance(response, dict):
                if 'results' in response:
                    response = self.to_csv(response['results'])
                else:
                    response = self.to_csv(response)

        return response
