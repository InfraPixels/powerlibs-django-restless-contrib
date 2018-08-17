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

        modified_ids = []
        failed_ids = {}

        for instance in queryset:
            changed = False
            try:
                for key, value in request.data.items():
                    old_value = getattr(instance, key, None)
                    if value != old_value:
                        setattr(instance, key, value)
                        changed = True

                if changed:
                    instance.save()

            except Exception as ex:
                the_type = ex.__class__.__name__
                failed_ids[instance.pk] = {
                    'error': the_type,
                    'message': f'{the_type}: {ex}',
                    'text': str(ex)
                }
                continue

            else:
                if changed:
                    modified_ids.append(instance.pk)

        return Http200({
            'count': count,
            'modified_ids': modified_ids,
            'modified_count': len(modified_ids),
            'failed_ids': failed_ids,
            'failed_count': len(failed_ids)
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

        deleted_ids = []

        for instance in queryset:
            instance = self.get_instance(request, *args, **kwargs)
            instance.delete()
            deleted_ids.append(instance.pk)

        return {
            'count': count,
            'deleted_ids': deleted_ids,
        }
