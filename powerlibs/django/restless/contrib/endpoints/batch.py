from powerlibs.django.restless.http import HttpError, Http200


SQS_MAX_MESSAGE_SIZE = 262144


def generate_payloads(affected_ids):
    payloads = []

    pivot_index = SQS_MAX_MESSAGE_SIZE // 20
    while len(affected_ids) > 0:
        part1 = affected_ids[:pivot_index]
        part2 = affected_ids[pivot_index:]

        payloads.append(part1)
        affected_ids = part2

    return payloads


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

        if count > 0:
            first_object = queryset.first()
            for sublist in generate_payloads(affected_ids):
                first_object.notify('batch_updated', {
                    'ids': sublist,
                    'total': count,
                })

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

        if count > 0:
            first_object = queryset.first()

        queryset.all().delete()

        if count > 0:
            for sublist in generate_payloads(affected_ids):
                first_object.notify('batch_deleted', {
                    'ids': sublist,
                    'total': count,
                })

        return {
            'count': count,
            'affected_ids': affected_ids,
        }


if __name__ == '__main__':
    ids = [x for x in range(0, 500)]
    print(generate_payloads(ids))
