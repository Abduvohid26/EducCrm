from django.utils import timezone
from .serializers import LoginSerializer, RegisterSerializer, ForgotSerializer, ResetPasswordSerializer
from django.contrib.auth import authenticate
from .models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework import permissions
from .regex import check_username_or_phone
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError


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
                    'data': [
                        {
                            'username': user.username,
                            'phone': user.phone
                        }
                    ],
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
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user_obj = serializer.save()
            data = {
                'username': user_obj.username,
                'phone': user_obj.phone,
                'tokens': [
                    {
                        'access_token': user_obj.token()['access_token'],
                        'refresh_token': user_obj.token()['refresh_token']
                    }
                ]
            }
            return Response(data=data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        code = request.data.get('code')
        self.check_verify(user=user, code=code)
        return Response(
            data={
                'success': True,
                'tokens':  [
                    {
                        'access_token': user.token()['access_token'],
                        'refresh_token': user.token()['refresh_token']
                    }
                ]
            }
        )
    @staticmethod
    def check_verify(user, code):
        verifies = user.verify_codes.filter(expired_at__gte=timezone.now(), confirmation_code=code, is_confirmed=False)
        if not verifies.exists():
            data = {
                'message': 'Verification code expired or error'
            }
            raise ValidationError(data)
        else:
            verify = verifies.first()
            verify.is_confirmed = True
            verify.save()
        return True


class GetNewVerifyCodeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        self.check_new_verify(user=user)
        user.create_verify_code()
        latest_code = user.verify_codes.order_by('-created_at').first()
        user.verify_codes.exclude(id=latest_code.id).delete()
        return Response(
            data={
                'success': True,
                'message': 'New code sent',
                'tokens': [
                    {
                        'access_token': user.token()['access_token'],
                        'refresh_token': user.token()['refresh_token']
                    }
                ]
            }
        )

    @staticmethod
    def check_new_verify(user):
        verifies = user.verify_codes.filter(expired_at__gte=timezone.now(), is_confirmed=False)
        if verifies.exists():
            raise ValidationError({
                'success': False,
                'message': 'Your code is still active'
            })
        return True

class GetCheckAPIView(APIView):
    def get(self, request, phone, chat_id):
        try:
            user = User.objects.get(phone=phone)
            latest_confirmation = user.verify_codes.order_by('-created_at').first()
            if latest_confirmation:
                code = latest_confirmation.confirmation_code
                user.chat_id = chat_id
                user.save()
                return Response(data={'code': code, 'chat_id': user.chat_id})
            else:
                return Response(data={'error': 'No confirmation code found'}, status=404)
        except User.DoesNotExist:
            return Response(data={'error': 'User not found'}, status=404)



class ForgotPasswordConfirmationAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ForgotSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        user.create_verify_code()
        latest_code = user.verify_codes.order_by('-created_at').first()
        user.verify_codes.exclude(id=latest_code.id).delete()
        return Response(
            {
                'success': True,
                'message': 'Verify code successfully send',
                'access': user.token()['access_token'],
                'refresh': user.token()['refresh_token']
            }
        )

import logging
logger = logging.getLogger(__name__)


class ResetPasswordAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            serializer.update(user, serializer.validated_data)
            return Response(
                {'success': True, 'message': 'Password successfully changed'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)