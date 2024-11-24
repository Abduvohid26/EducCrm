from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.utils import timezone
import random

class User(AbstractUser):
    phone = models.CharField(max_length=200, unique=True)
    photo = models.ImageField(upload_to='users_photos/', null=True, blank=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png','gif', 'jpeg'])])
    chat_id = models.CharField(max_length=20)

    @property
    def full_data(self):
        return f'{self.first_name} {self.last_name} {self.phone} {self.username}'


    def __str__(self):
        return f'{self.full_data}'

    def check_password_hash(self):
        if not self.password.startswith('pbkdf2_sha'):
            self.set_password(self.password)


    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token)
        }

    def create_verify_code(self):
        code = "".join([str(random.randint(0,100) % 10) for _ in range(4)])
        UserConfirmation.objects.create(
            user=self,
            confirmation_code=code,
        )
        return code

    def save(self, *args, **kwargs):
        self.check_password_hash()
        super().save(*args, **kwargs)



class UserConfirmation(models.Model):
    user = models.ForeignKey(User, related_name='verify_codes', on_delete=models.CASCADE)
    confirmation_code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(null=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - {self.confirmation_code}'

    def save(self, *args, **kwargs):
        self.expired_at = timezone.now() + timedelta(minutes=4)
        super(UserConfirmation, self).save(*args, **kwargs)


