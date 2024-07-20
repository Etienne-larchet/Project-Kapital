from rest_framework import serializers
from .models import GeneralModel, SecSearch


# decorator
def inherit_fields(base_serializer):
    def decorator(serializer_cls):
        class WrappedSerializer(serializer_cls):
            class Meta(serializer_cls.Meta):
                model = serializer_cls.Meta.model
                fields = getattr(base_serializer.Meta, 'fields', []) + getattr(serializer_cls.Meta, 'fields', [])
                extra_kwargs = {**getattr(base_serializer.Meta, 'extra_kwargs', {}), **getattr(serializer_cls.Meta, 'extra_kwargs', {})}
        return WrappedSerializer
    return decorator


class GeneralModelSerializer(serializers.ModelSerializer): #WIP if share params are needed // May be useless if use of cookies
    class Meta:
        model = GeneralModel
        fields = []
        extra_kwargs = {}


@inherit_fields(GeneralModelSerializer)
class SecSearchSerializer(serializers.ModelSerializer):
    class Meta():
        model = SecSearch
        fields = ['ticker', 'fromDate', 'toDate', 'formType']
        extra_kwargs = {
            'fromDate': {'required': False},
            'toDate': {'required': False},
            'formType': {'required': False}
        }