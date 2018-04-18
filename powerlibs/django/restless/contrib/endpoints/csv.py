import csv
from io import StringIO
import json

from powerlibs.django.restless.http import JSONResponse


class CSVListEndpointMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._csv_fieldnames = None

    def get_csv_fieldnames(self, entry):
        if self._csv_fieldnames is None:
            self._csv_fieldnames = tuple(key for key in entry.keys())
        return self._csv_fieldnames

    def to_csv(self, results):
        if len(results) == 0:
            return ''

        fieldnames = self.get_csv_fieldnames(results[0])
        the_buffer = StringIO()

        csv_writer = csv.DictWriter(the_buffer, fieldnames=fieldnames)
        csv_writer.writerows(results)

        the_buffer.seek(0)
        return the_buffer.read()

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        accept = request.META.get('accept', None)
        if 'text/csv' in accept:

            if isinstance(response, JSONResponse):
                serialized_data = json.loads(response.content)
                if 'results' in serialized_data:
                    csv_data = self.to_csv(serialized_data['results'])
                else:
                    csv_data = self.to_csv(serialized_data)

                response.content = json.dumps(csv_data)

            elif isinstance(response, dict):
                response = self.to_csv(response)

        return response
