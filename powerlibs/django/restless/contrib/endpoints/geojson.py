import json

import shapely.wkt
import shapely.geometry

from powerlibs.django.restless.http import JSONResponse


SQS_MAX_MESSAGE_SIZE = 262144


class GeoJSONEndpointMixin:
    def get_geometry_fields_and_types(self):
        for field in self.model._meta.fields:
            class_name = field.__class__.__name__
            if class_name in ('PointField', 'LineStringField', 'PolygonField'):
                yield (field.name, class_name)

    def generate_geojson(self, obj):
        geometries = [(geometry_field_name, geometry_type) for geometry_field_name, geometry_type in self.get_geometry_fields_and_types()]

        for geometry_field_name, _ in geometries:
            new_field_name = geometry_field_name + '__geojson'

            value = obj[geometry_field_name]

            if len(str(value)) > SQS_MAX_MESSAGE_SIZE / 3:
                obj[geometry_field_name] = None

            if value is None:
                obj[new_field_name] = value
                continue

            feature_str = value
            if ';' in feature_str:
                _, feature_str = value.split(';')
            feature = shapely.wkt.loads(feature_str)

            geojson = shapely.geometry.mapping(feature)
            if len(str(geojson)) > (SQS_MAX_MESSAGE_SIZE / 3):
                obj[new_field_name] = None
            else:
                obj[new_field_name] = geojson

    def serialize(self, objects):
        serialized_objects = super().serialize(objects)

        if type(serialized_objects) in (list, tuple):
            for obj in serialized_objects:
                self.generate_geojson(obj)
        else:
            self.generate_geojson(serialized_objects)

        return serialized_objects

    def hydrate_data_geojson(self, data):
        for geometry_field_name, _ in self.get_geometry_fields_and_types():
            field_name_as_geojson = geometry_field_name + '__geojson'
            value = data.pop(field_name_as_geojson, None)
            if value:
                data[geometry_field_name] = shapely.geometry.asShape(value).wkt
        return data


class GeoJSONDetailEndpointMixin(GeoJSONEndpointMixin):
    def get(self, request, *args, **kwargs):
        serialized_data = self.serialize(self.get_instance(request, *args, **kwargs))

        instance = self.get_instance(request, *args, **kwargs)
        for geometry_field_name, _ in self.get_geometry_fields_and_types():
            new_field_name = geometry_field_name + '__geojson'
            value = getattr(instance, geometry_field_name)
            if value:
                serialized_data[new_field_name] = json.loads(value.geojson)

        return serialized_data

    def put(self, request, *args, **kwargs):
        self.hydrate_data_geojson(request.data)
        return self.hydrate_output_geojson(super().put(request, *args, **kwargs))

    def patch(self, request, *args, **kwargs):
        self.hydrate_data_geojson(request.data)
        return self.hydrate_output_geojson(super().patch(request, *args, **kwargs))

    def hydrate_output_geojson(self, response):
        if isinstance(response, JSONResponse):
            serialized_data = json.loads(response.content)
            for geometry_field_name, _ in self.get_geometry_fields_and_types():
                new_field_name = geometry_field_name + '__geojson'
                value = serialized_data.get(geometry_field_name, None)
                if value is None:
                    serialized_data[new_field_name] = None
                elif isinstance(value, str):

                    v = value
                    if ';' in value:
                        v = value.split(';')[1]
                    feature = shapely.wkt.loads(v)
                    serialized_data[new_field_name] = shapely.geometry.mapping(feature)
                else:
                    serialized_data[new_field_name] = json.loads(value.geojson)
            response.content = json.dumps(serialized_data)

        return response


class GeoJSONListEndpointMixin(GeoJSONEndpointMixin):
    def post(self, request, *args, **kwargs):
        self.hydrate_data_geojson(request.data)
        return super().post(request, *args, **kwargs)
