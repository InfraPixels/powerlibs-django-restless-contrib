from shapely.geometry import box


class BoundingBoxListEndpointMixin:
    def get_query_set(self, request, *args, **kwargs):
        used_keys = []
        queryset_args = {}

        for key, value in request.GET.items():
            if key.endswith('__bbox'):
                field_name = key.replace('__bbox', '')
                bbox_coords = tuple(float(x) for x in value.split(','))
                bbox = box(*bbox_coords)
                field_arg_name = f'{field_name}__within'
                queryset_args[field_arg_name] = bbox.to_wkt()
                used_keys.append(key)

        if used_keys:
            request.GET._mutable = True
            for key in used_keys:
                del request.GET[key]

        queryset = super().get_query_set(request, *args, **kwargs)
        queryset = queryset.filter(**queryset_args)

        return queryset
