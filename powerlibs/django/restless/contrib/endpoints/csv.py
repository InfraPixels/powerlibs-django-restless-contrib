import csv
from io import StringIO
import json

from django.http import HttpResponse

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
