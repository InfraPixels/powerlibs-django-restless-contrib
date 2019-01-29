from django.core.exceptions import FieldError
from django.core.validators import ValidationError
from django.db.models import Q

from powerlibs.django.restless.http import Http400, HttpError


class AncestryEndpointMixin:
    def get_ancestors(self, ancestry_field, instance_data):
        current_generation = instance_data
        while True:
            ancestor_id = current_generation[ancestry_field]
            if ancestor_id is None:
                break

            parent_object = self.model.objects.get(id=ancestor_id)
            current_generation = parent_object.serialize()
            yield current_generation

    def get(self, request, *args, **kwargs):
        data = super().get(request, *args, **kwargs)

        ancestry_field = request.GET.get('_show_ancestry')
        if ancestry_field:
            if isinstance(data, dict):
                if 'results' in data:
                    results = data['results']
                    current_ids = [item['id'] for item in results]

                    for item in data['results']:
                        ancestors = self.get_ancestors(ancestry_field, item)

                        for item in ancestors:
                            item_id = item['id']
                            if item_id not in current_ids:
                                results.append(item)
                                current_ids.append(item_id)

                    if 'count' in data:
                        data['count'] = len(current_ids)
                else:
                    ancestors = self.get_ancestors(ancestry_field, data)
                    data['_ancestors'] = list(ancestors)

        return data
