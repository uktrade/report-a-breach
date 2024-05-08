from core.models import BaseModel
from django.db import models


class Users(BaseModel):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_pending = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
