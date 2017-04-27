from cached_property import cached_property

from powerlibs.django.restless.models import serialize_model


class NestedEntitiesMixin:
    @cached_property
    def foreign_keys(self):
        fields = []
        for field in self.model._meta.fields:
            class_name = field.__class__.__name__
            if class_name == 'ForeignKey':
                fields.append(field.name)

        return fields


class NestedEntitiesDetailEndpointMixin(NestedEntitiesMixin):
    def get(self, request, *args, **kwargs):
        serialized_data = super().get(request, *args, **kwargs)

        nesting_request = request.GET.get('_nested', None)
        if nesting_request:
            serialized_data['_related'] = related_entities = {}
            instance = self.get_instance(request, *args, **kwargs)
            for entity_name in nesting_request.split(','):
                if entity_name in self.foreign_keys:
                    entity = getattr(instance, entity_name)
                    try:
                        serialized_entity = entity.serialize()
                    except AttributeError:
                        serialized_entity = serialize_model(entity)
                    related_entities[entity_name] = serialized_entity

        return serialized_data


class NestedEntitiesListEndpointMixin(NestedEntitiesMixin):
    def get(self, request, *args, **kwargs):
        results = super().get(request, *args, **kwargs)

        nesting_request = request.GET.get('_nested', None)
        if not nesting_request:
            return results

        is_paginated = isinstance(results, dict) and 'results' in results

        if is_paginated:
            items = results['results']
        else:
            items = results

        for item in items:
            item['_related'] = related_entities = {}

            for entity_name in nesting_request.split(','):
                if entity_name in self.foreign_keys:
                    field = getattr(self.model, entity_name)
                    entity_id = item[entity_name]

                    entity = field.get_queryset().get(id=entity_id)
                    try:
                        serialized_entity = entity.serialize()
                    except AttributeError:
                        serialized_entity = serialize_model(entity)
                    related_entities[entity_name] = serialized_entity

        return results
