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

    def get(self, request, *args, **kwargs):
        data = super().get(request, *args, **kwargs)

        ancestry_field = request.GET.get('_show_ancestry')
        if ancestry_field:
            if isinstance(data, dict):
                if 'results' in data:
                    results = data['results']
                    current_ids = [item['id'] for item in results]

                    ancestors_ids = [item[ancestry_field] for item in results
                            if item[ancestry_field] is not None]

                    ancestors_cache = {}
                    for item in self.model.objects.filter(id__in=ancestors_ids):
                        ancestors_cache[item.id] = item.serialize()

                    for item in data['results']:
                        ancestors = self.get_ancestors(
                            ancestry_field,
                            item,
                            ancestors_cache
                        )

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
