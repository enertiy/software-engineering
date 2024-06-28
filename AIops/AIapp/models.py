from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
class UserManager(models.Manager):
    def create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        if not password:
            raise ValueError('The Password field must be set')

        # 使用 make_password 函数对密码进行哈希处理
        # hashed_password = make_password(password)
        # user = self.model(username=username, password=hashed_password, **extra_fields)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, username):
        return self.get(username=username)
# Create your models here.
class User(models.Model):
    username=models.CharField(max_length=100,null=False,unique=True)
    password=models.CharField(max_length=100,null=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)
    def __str__(self):
        return self.username
class Admin(models.Model):
    username = models.CharField(max_length=100, null=False, unique=True)
    password = models.CharField(max_length=100, null=False)

    def __str__(self):
        return self.username


class Comment(models.Model):
    username = models.CharField(max_length=100)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username}: {self.comment[:20]}"

class Submission(models.Model):
    username = models.CharField(max_length=150)
    file_name = models.CharField(max_length=255)
    upload_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.file_name}"
