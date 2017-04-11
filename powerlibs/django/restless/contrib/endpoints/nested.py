from cached_property import cached_property


class NestedEntitiesMixin:
    pass


class NestedEntitiesDetailEndpointMixin(NestedEntitiesMixin):
    @cached_property
    def foreign_keys(self):
        for field in self.model._meta.fields:
            class_name = field.__class__.__name__
            if class_name == 'ForeignKey':
                yield field.name

    def get(self, request, *args, **kwargs):
        serialized_data = super().get(request, *args, **kwargs)

        nesting_request = request.GET.get('_nested', None)
        if nesting_request:
            serialized_data['_related'] = related_entities = {}
            instance = self.get_instance(request, *args, **kwargs)
            for entity_name in nesting_request.split(','):
                if entity_name in self.foreign_keys:
                    entity = getattr(instance, entity_name)
                    serialized_entity = self.serialize(entity)
                    related_entities[entity_name] = serialized_entity

        return serialized_data
