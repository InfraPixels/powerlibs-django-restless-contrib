from cached_property import cached_property

from django.conf import settings


class PaginatedEndpointMixin:
    def get(self, request, *args, **kwargs):
        limit = int(request.GET.get('_limit') or settings.DEFAULT_PAGE_SIZE)
        offset = int(request.GET.get('_offset') or 0)

        begin = offset
        end = begin + limit

        qs = self.get_query_set(request, *args, **kwargs)
        total = qs.count()

        paginated_qs = qs[begin:end]
        count = paginated_qs.count()

        serialized_results = self.serialize(paginated_qs)

        return {
            'total': total,
            'count': count,
            'results': serialized_results,
        }


class OrderedEndpointMixin:
    def get_query_set(self, request, *args, **kwargs):
        queryset = super().get_query_set(request, *args, **kwargs)

        if '_orderby' in request.GET:
            orderby_field = request.GET['_orderby']
            queryset = queryset.order_by(orderby_field)

        return queryset


class FilteredEndpointMixin:
    @cached_property
    def model_fields(self):
        return tuple(f.name for f in self.model._meta.fields)

    def get_query_set(self, request, *args, **kwargs):
        queryset = super().get_query_set(request, *args, **kwargs)

        filter_args = {}
        for key, value in request.GET.items():
            if key.startswith('_'):
                continue

            field_name = key.split('__')[0]
            if field_name in self.model_fields:
                filter_args[key] = value

        return queryset.filter(**filter_args)


class SoftDeletableDetailEndpointMixin:
    def delete(self, request, *args, **kwargs):
        instance = self.get_instance(request, *args, **kwargs)

        old_deleted_status = instance.deleted
        if not old_deleted_status:
            instance.deleted = True
            instance.save()

        return {}


class SoftDeletableListEndpointMixin:
    def get_query_set(self, request, *args, **kwargs):
        queryset = super().get_query_set(request, *args, **kwargs)
        return queryset.filter(deleted=False)
