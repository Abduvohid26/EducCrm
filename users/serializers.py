from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    username_or_phone = serializers.CharField(max_length=200)
    password = serializers.CharField(max_length=128, write_only=True)