from rest_framework import serializers

from users.models import User
from rest_framework.exceptions import ValidationError

class LoginSerializer(serializers.Serializer):
    username_or_phone = serializers.CharField(max_length=200)
    password = serializers.CharField(max_length=128, write_only=True)


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'phone', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.create_verify_code()
        return user

    def validate_username(self, value):
        value = value.lower()
        if value and User.objects.filter(username=value).exists():
            data = {
                'success': False,
                'message': f'This is {value} already registered'
            }
            raise ValidationError(data)
        return value
    def validate_phone(self, value):
        if value and User.objects.filter(phone=value).exists():
            data = {
                'success': False,
                'message': f'This phone number {value} is already registered'
            }
            raise ValidationError(data)
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters")
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("Password must contain at least one letter.")
        return value


class ForgotSerializer(serializers.Serializer):
    phone = serializers.CharField(write_only=True, required=True)
    def validate(self, attrs):
        phone = attrs.get('phone')
        if phone is None:
            raise serializers.ValidationError("Invalid Phone number")
        user = User.objects.filter(phone=phone)
        if not user.exists():
            raise serializers.ValidationError("User does not exist")
        attrs['user'] = user.first()
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128, write_only=True)
    password_confirm = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        password = data.get('password')
        password_confirm = data.get('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters.")
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("Password must contain at least one letter.")
        return value

    def update(self, instance, validated_data):
        validated_data.pop('password_confirm', None)
        instance.set_password(validated_data['password'])
        instance.save()
        return instance
