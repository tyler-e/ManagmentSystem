from __future__ import annotations

import requests

from django.db import models

from typing import Dict

from canvasapi import Canvas
from canvasapi.user import User as CanvasUser


# Create your models here.
class SpaceUser(models.Model):
    niner_id = models.IntegerField(primary_key=True)
    first_name = models.TextField(blank=True, null=True)
    last_name = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    canvas_id = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.first_name}, {self.last_name}"
    
    def __repr__(self):
        return f"space_user({self.niner_id}, {self.first_name}, {self.last_name}, {self.email}, {self.canvas_id})" + super().__repr__()
    
    def niner_engage_get_updated_values(self, config:Dict[str, str]) -> SpaceUser:
        if self.first_name and self.last_name and self.email:
            if "t" in config.get("VERBOSE_DEBUG", "false").lower(): print(f"Values Already set, shouldnt have run")
            return self
        url = "https://ninerengage.charlotte.edu/api/discovery/swipe/attendance"
        headers = {"Cookie": config["NINER_ENGAGE_COOKIE"],
               "X-Xsrf-Token": config["NINER_ENGAGE_TOKEN"]}
        data = {
            "swipe": self.niner_id,
            "token": config["NINER_ENGAGE_PAYLOAD_TOKEN"]
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            val_dic = response.json()
            self.first_name = val_dic["user"]["firstName"]
            self.last_name = val_dic["user"]["lastName"]
            self.email = val_dic["user"]["campusEmail"]
            self.save()
        else:
            if "t" in config.get("VERBOSE_DEBUG", "false").lower(): print(f"response: {response.status_code} -- {response.text}")
        return self
    
    def get_canvas_id_from_canvas(self, config:Dict[str, str]) -> SpaceUser:
        if self.canvas_id:
            return self
        canvas = Canvas("https://instructure.charlotte.edu", config["CANVAS_API_KEY"])
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




