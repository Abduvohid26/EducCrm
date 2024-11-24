from django.shortcuts import render
from .serializers import LoginSerializer
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework import permissions
from .regex import check_username_or_phone

class LoginAPIView(CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            username_or_phone = serializer.validated_data['username_or_phone']
            password = serializer.validated_data['password']
            checks = check_username_or_phone(username_or_phone)
            user = None
            if checks == 'phone':
                user_obj = User.objects.filter(phone=username_or_phone).first()
                if user_obj:
                    username = user_obj.username
                    user = authenticate(request, username=username, password=password)
            else:
                user = authenticate(request, username=username_or_phone, password=password)

            if user is not None:
                data = {
                    'success': True,
                    'message': 'User successfully logged in',
                    'tokens': [
                        {
                            'access_token': user.token()['access_token'],
                            'refresh_token': user.token()['refresh_token']
                        }
                    ]
                }
                return Response(data=data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Login yoki parol noto\'g\'ri'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class RegisterAPIView(CreateAPIView):
    pass