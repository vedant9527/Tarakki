from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, user_type='student'):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            user_type=user_type
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=email,
            username=username,
            password=password,
            user_type='admin'
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    USER_TYPES = [
        ('student', 'Student'),
        ('mentor', 'Mentor'),
        ('admin', 'Admin'),
    ]

    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='student')
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True



class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    prediction = models.CharField(max_length=100,null=True)  
    scores = models.JSONField(null=True)

    def __str__(self):
        return self.user.username
    
class Profession(models.Model):
    pass

class MentorProfile(models.Model):
    pass

class TestResults(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)







class Question(models.Model):
    parameter = models.CharField(max_length=50)
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1)