from rest_framework import serializers

from .models import Connection


class ConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connection
        fields = ["new_user", "email", "password"]
        extra_kwargs = {"new_user": {"required": False, "default": False}}
