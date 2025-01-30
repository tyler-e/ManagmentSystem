from __future__ import annotations

import requests

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import FileExtensionValidator

from django.utils.timezone import now, localtime


from typing import Dict, Tuple

from canvasapi import Canvas
from canvasapi.user import User as CanvasUser

import os


class SpaceUserManager(BaseUserManager):
    def create_user(self, niner_id, password=None, **extra_fields) -> SpaceUser:
        if not niner_id:
            raise ValueError('The Niner ID must be set')
        user = self.model(niner_id=niner_id, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, niner_id, password=None, **extra_fields) -> SpaceUser:
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Create the superuser using the create_user method
        return self.create_user(niner_id, password, **extra_fields)

    def get_or_create(self, niner_id) -> Tuple[SpaceUser, bool]:
        user = self.filter(niner_id=niner_id).first()
        if user:
            return (user, False)

        user = self.model(niner_id=niner_id)
        user.save()
        return (user, True)

    

# Create your models here.
class SpaceUser(AbstractBaseUser, PermissionsMixin):
    niner_id = models.IntegerField(primary_key=True)
    canvas_id = models.IntegerField(blank=True, null=True)
    first_name = models.TextField(blank=True, null=True)
    last_name = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    user_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    
    class SpaceLevel(models.IntegerChoices):
        USER = 0
        VOLUNTEER = 30
        KEYHOLDER = 70
        STAFF = 100
    
    space_level = models.IntegerField(choices=SpaceLevel.choices, default=SpaceLevel.USER)
    keyholder_priority = models.IntegerField(default=-10)
    
    USERNAME_FIELD="niner_id"
    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    groups = models.ManyToManyField('auth.Group', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', blank=True)

    
    objects = SpaceUserManager()
    
    def get_full_name(self) -> str:
        return f"{self.first_name}, {self.last_name}"
    
    def get_short_name(self) -> str:
        return f"{self.first_name}"
    
    def __str__(self):
        return self.get_full_name()
    
    def __eq__(self, value):
        if isinstance(value, SpaceUser):
            return self.niner_id == value.niner_id
        return False

    def __hash__(self):
        return hash(self.niner_id)
    
    def __repr__(self):
        return f"space_user({self.niner_id}, {self.first_name}, {self.last_name}, {self.email}, {self.canvas_id})" + super().__repr__()
    
    def niner_engage_get_updated_values(self) -> SpaceUser:
        if self.first_name and self.last_name and self.email:
            print(f"Values Already set, shouldnt have run")
            return self
        url = "https://ninerengage.charlotte.edu/api/discovery/swipe/attendance"
        cookies = {cookie.split("=")[0]: cookie.split("=")[1] for cookie in os.getenv("NINER_ENGAGE_COOKIE").split("; ")}
        headers = {"X-Xsrf-Token": os.getenv("NINER_ENGAGE_TOKEN")}
        data = {
            "swipe": self.niner_id,
            "token": os.getenv("NINER_ENGAGE_PAYLOAD_TOKEN")
        }
        response = requests.post(url, headers=headers, cookies=cookies, json=data)
        if response.status_code == 200:
            val_dic = response.json()
            print(val_dic)
            if not val_dic.get("user", None):
                return self
            self.first_name = val_dic["user"]["firstName"]
            self.last_name = val_dic["user"]["lastName"]
            self.email = val_dic["user"]["campusEmail"]
            self.save()
        else:
            print(f"response: {response.status_code} -- {response.text}")
        return self
    
    def get_canvas_id_from_canvas(self) -> SpaceUser:
        if self.canvas_id:
            return self
        canvas = Canvas("https://instructure.charlotte.edu", os.getenv("CANVAS_API_KEY"))
        course = canvas.get_course(231237)
        for couse_user in course.get_users():
            couse_user: CanvasUser
            profile = couse_user.get_profile()
            if profile["primary_email"] == self.email:
                self.canvas_id = profile["id"]
                break
        
        if not self.canvas_id:
            print("SEND CANVAS EMAIL HERE")
            return self#Send email invite?
        else:
            self.save()
            return self

class KeyolderHistoryManager(models.Manager):
    def get_current_keyholder(self) -> KeyholderHistory:
        return KeyholderHistory.objects.filter(exit_time__isnull=True).order_by('-start_time').first()
    def is_keyholder(self, user:SpaceUser) -> bool:
        return user.space_level >= user.SpaceLevel.KEYHOLDER  
    def can_open(self, user:SpaceUser) -> bool:
        return user.space_level >= user.SpaceLevel.VOLUNTEER
    def create_keyholder_history(self, user:SpaceUser) -> KeyholderHistory:
        if self.can_open(user):
            keyholder_history = self.create(keyholder=user, start_time=now())
            return keyholder_history
        else:
            raise ValueError("User must be a keyholder")
class KeyholderHistory(models.Model):
    keyholder = models.ForeignKey(SpaceUser, on_delete=models.CASCADE, related_name="keyholder_history")
    start_time = models.DateTimeField()
    exit_time = models.DateTimeField(null=True, blank=True)
    objects = KeyolderHistoryManager()