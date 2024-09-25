import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser

from api_v1.utils import LowercaseCharField


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-updated_at", "-created_at"]


class User(BaseModel):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_active = models.BooleanField(null=True)
    last_login = models.DateTimeField(null=True)


class Admin(AbstractBaseUser, BaseModel):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]


class Book(BaseModel):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=255)
    published_date = models.DateField()
    publisher = models.CharField(max_length=50)
    category = LowercaseCharField(max_length=50)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class BorrowedBook(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrowed_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()

    def __str__(self):
        return f"{self.user.email} borrowed {self.book.title}"
