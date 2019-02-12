from django.core.exceptions import FieldError
from django.core.validators import ValidationError
from django.db.models import Q

from powerlibs.django.restless.http import Http400, HttpError


class AncestryEndpointMixin:
    def get_ancestors(self, ancestry_field, instance_data, cache=None):
        cache = cache or {}

        current_generation = instance_data
        while True:
            ancestor_id = current_generation[ancestry_field]
            if ancestor_id is None:
                break

            if ancestor_id in cache:
                current_generation = cache[ancestor_id]
            else:
                parent_object = self.model.objects.get(id=ancestor_id)
                current_generation = parent_object.serialize()
                cache[parent_object.id] = current_generation

            yield current_generation

    def fill_list_with_ancestors(self, data, ancestry_field):
        results = data['results']
        current_ids = [item['id'] for item in results]
        current_collection = list(data['results'])

        while True:
            ancestors_ids = [item[ancestry_field] for item in current_collection
                    if item[ancestry_field] is not None and
                    item[ancestry_field] not in current_ids]

            if not ancestors_ids:
                break

            current_collection = []
            for item in self.model.objects.filter(id__in=ancestors_ids):
                serialized_item = item.serialize()
                current_collection.append(serialized_item)
                current_ids.append(item.id)
                results.append(serialized_item)

        if 'count' in data:
            data['count'] = len(current_ids)

    def get(self, request, *args, **kwargs):
        data = super().get(request, *args, **kwargs)

        ancestry_field = request.GET.get('_show_ancestry')
        if ancestry_field:
            if isinstance(data, dict):
                if 'results' in data:
                    self.fill_list_with_ancestors(data, ancestry_field)
                else:
                    ancestors = self.get_ancestors(ancestry_field, data)
                    data['_ancestors'] = list(ancestors)

        return data
