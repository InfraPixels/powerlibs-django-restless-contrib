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

    @staticmethod
    def get_hidden_fields(model):
        fields = []
        for field in model._meta.fields:
            class_name = field.__class__.__name__
            if class_name == 'PasswordField' or field.name == 'password':
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

                    if entity:
                        serialized_entity = serialize_model(entity, exclude=self.get_hidden_fields(entity._meta.model))
                    else:
                        serialized_entity = None

                    related_entities[entity_name] = serialized_entity
                    continue

                field = getattr(instance, entity_name, None)

                if field and field.__class__.__name__ == 'ManyRelatedManager':
                    the_list = related_entities[entity_name] = []

                    for entity in field.all():
                        the_list.append(serialize_model(entity, exclude=self.get_hidden_fields(entity._meta.model)))

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

                    alt_name = f'{entity_name}_id'
                    if alt_name in item:
                        entity_id = item[alt_name]
                    else
                        entity_id = item[entity_name]

                    if not entity_id:
                        related_entities[entity_name] = None
                        continue

                    entity = field.get_queryset().get(id=entity_id)
                    serialized_entity = serialize_model(entity, exclude=self.get_hidden_fields(entity._meta.model))
                    related_entities[entity_name] = serialized_entity
                    continue

                field = getattr(self.model, entity_name, None)

                if field and field.__class__.__name__ == 'ManyToManyDescriptor':
                    the_list = related_entities[entity_name] = []

                    item_entity = self.model.objects.filter(id=item['id']).prefetch_related(entity_name)[0]
                    manager = getattr(item_entity, entity_name)

                    for entity in manager.all():
                        the_list.append(serialize_model(entity, exclude=self.get_hidden_fields(entity._meta.model)))

        return results
