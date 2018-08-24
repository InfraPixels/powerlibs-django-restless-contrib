from powerlibs.django.restless.http import HttpError, Http200


class BatchOperationsMixin:
    def patch(self, request, *args, **kwargs):
        if 'PATCH' not in self.methods:
            raise HttpError(405, 'Method Not Allowed')

        # This is to avoid screwing up the database because of
        # stupid front-end mistakes, like forgetting to append
        # the object ID at the end of the URL:
        batch_enabled = request.GET.get('_batch', None)
        if batch_enabled is None or str(batch_enabled).lower() != 'true':
            raise HttpError(405, 'Method Not Allowed')

        queryset = super().get_query_set(request, *args, **kwargs)
        count = queryset.count()

        affected_ids = [item.id for item in queryset]

        data = dict(request.data)
        data.pop('organization', None)
        data.pop('organization_id', None)
        data.pop('created_by', None)
        data.pop('created_by_id', None)
        data.pop('updated_by', None)
        data.pop('updated_by_id', None)

        queryset.all().update(**data)

        return Http200({
            'count': count,
            'affected_ids': affected_ids,
            'affected_ids_count': len(affected_ids),
        })

    def delete(self, request, *args, **kwargs):
        if 'DELETE' not in self.methods:
            raise HttpError(405, 'Method Not Allowed')

        # This is to avoid screwing up the database because of
        # stupid front-end mistakes, like forgetting to append
        # the object ID at the end of the URL:
        batch_enabled = request.GET.get('_batch', None)
        if batch_enabled is None or str(batch_enabled).lower() != 'true':
            raise HttpError(405, 'Method Not Allowed')

        queryset = super().get_query_set(request, *args, **kwargs)
        count = queryset.count()

        affected_ids = [item.id for item in queryset]

        queryset.all().delete()

        return {
            'count': count,
            'affected_ids': affected_ids,
        }
