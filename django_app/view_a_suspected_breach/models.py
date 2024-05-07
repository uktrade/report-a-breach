from core.models import BaseModel
from django.db import models


class User(BaseModel):
    email = models.EmailField(unique=True)
    is_pending = models.BooleanField(default=True)


class AdminUser(BaseModel):
    email = models.EmailField(unique=True)
