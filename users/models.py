from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from rest_framework_simplejwt.tokens import RefreshToken


class User(AbstractUser):
    phone = models.CharField(max_length=200, unique=True)
    photo = models.ImageField(upload_to='users_photos/', null=True, blank=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png','gif', 'jpeg'])])

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


    def save(self, *args, **kwargs):
        self.check_password_hash()
        super().save(*args, **kwargs)
