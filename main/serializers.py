from rest_framework import serializers


class IPSerializer(serializers.Serializer):
    ip = serializers.IPAddressField()
