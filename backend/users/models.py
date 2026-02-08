from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    driver_license_image = models.ImageField(
        upload_to="driver_licenses/",
        null=True,
        blank=True
    )

    phone_number = models.CharField(
        max_length=15,
        null=True,
        blank=True
    )

    address = models.TextField(
        null=True,
        blank=True
    )

    # created_at = models.DateTimeField(auto_now_add=True)  Kế thừa từ users của django có sẵn date_joined

    def __str__(self):
        return self.username
