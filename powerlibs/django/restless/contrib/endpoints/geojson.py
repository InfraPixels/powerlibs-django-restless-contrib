import json

import shapely.wkt
import shapely.geometry


class GeoJSONEndpointMixin:
    def get_geometry_fields_and_types(self):
        for field in self.model._meta.fields:
            class_name = field.__class__.__name__
            if class_name in ('PointField', 'LineStringField', 'PolygonField'):
                yield (field.name, class_name)


class GeoJSONDetailEndpointMixin(GeoJSONEndpointMixin):
    def get(self, request, *args, **kwargs):
        serialized_data = self.serialize(self.get_instance(request, *args, **kwargs))

        instance = self.get_instance(request, *args, **kwargs)
        for geometry_field_name, geometry_type in self.get_geometry_fields_and_types():
            new_field_name = geometry_field_name + '__geojson'
            value = getattr(instance, geometry_field_name)
            serialized_data[new_field_name] = json.loads(value.geojson)

        return serialized_data


class GeoJSONListEndpointMixin(GeoJSONEndpointMixin):
    def serialize(self, objects):
        serialized_objects = super().serialize(objects)
        geometries = [(geometry_field_name, geometry_type) for geometry_field_name, geometry_type in self.get_geometry_fields_and_types()]

        def generate_geojson(obj):
            for geometry_field_name, geometry_type in geometries:
                new_field_name = geometry_field_name + '__geojson'

                value = obj[geometry_field_name]

                if value is None:
                    obj[new_field_name] = value
                    continue

                feature_str = value
                if ';' in feature_str:
                    _, feature_str = value.split(';')
                feature = shapely.wkt.loads(feature_str)
                obj[new_field_name] = shapely.geometry.mapping(feature)

        if type(serialized_objects) in (list, tuple):
            for obj in serialized_objects:
                generate_geojson(obj)
        else:
            generate_geojson(serialized_objects)

        return serialized_objects

    def post(self, request, *args, **kwargs):
        for geometry_field_name, geometry_type in self.get_geometry_fields_and_types():
            field_name_as_geojson = geometry_field_name + '__geojson'
            value = request.data.pop(field_name_as_geojson, None)
            if value:
                request.data[geometry_field_name] = shapely.geometry.asShape(value).wkt

        return super().post(request, *args, **kwargs)
