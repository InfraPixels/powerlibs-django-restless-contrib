from shapely.geometry import box


class BoundingBoxListEndpointMixin:
    def get_query_set(self, request, *args, **kwargs):
        queryset = super().get_query_set(request, *args, **kwargs)

        for key, value in request.GET.items():
            if key.endswith('__bbox'):
                field_name = key.replace('__bbox', '')
                bbox_coords = tuple(float(x) for x in value.split(','))
                bbox = box(bbox_coords)
                field_arg_name = f'{field_name}__within'
                queryset = queryset.filter(**{field_arg_name: bbox.to_wkt()})

        return queryset
