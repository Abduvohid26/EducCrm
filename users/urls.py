from . import views
from django.urls import path


urlpatterns = [
    path('login/', views.LoginAPIView.as_view()),
    path('register/', views.RegisterAPIView.as_view()),
    path('verify/', views.VerifyAPIView.as_view()),
    path('new-verify/', views.GetNewVerifyCodeAPIView.as_view()),
    path('forget-password/', views.ForgotPasswordConfirmationAPIView.as_view()),
    path('reset-password/', views.ResetPasswordAPIView.as_view(), name='reset-password'),
    path('get-check/<str:phone>/<str:chat_id>/', views.GetCheckAPIView.as_view(), name='get_check'),
]