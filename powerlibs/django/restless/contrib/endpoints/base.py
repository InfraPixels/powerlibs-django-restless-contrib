from cached_property import cached_property

from django.conf import settings
from django.forms.models import model_to_dict

from powerlibs.django.restless.http import HttpError, Http200
from powerlibs.django.restless.modelviews import DetailEndpoint as RestlessDetailEndpoint, _get_form


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


class FilteredEndpointMixin:
    @cached_property
    def model_fields(self):  # pragma: no cover
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


class SoftDeletableEndpointMixin:
    def delete(self, request, *args, **kwargs):
        instance = self.get_instance(request, *args, **kwargs)

        old_deleted_status = instance.deleted
        if not old_deleted_status:
            instance.deleted = True
            instance.save()

        return {}


class DetailEndpoint(RestlessDetailEndpoint):
    def patch(self, request, *args, **kwargs):
        """Update the object represented by this endpoint."""

        # if 'PATCH' not in self.methods:
        #     raise HttpError(405, 'Method Not Allowed')

        Form = _get_form(self.form, self.model)
        instance = self.get_instance(request, *args, **kwargs)

        form_data = model_to_dict(instance)
        form_data.update(request.data)

        form = Form(
            form_data,
            request.FILES,
            instance=instance
        )
        if form.is_valid():
            obj = form.save()
            return Http200(self.serialize(obj))
        raise HttpError(400, 'Invalid data', errors=form.errors)
