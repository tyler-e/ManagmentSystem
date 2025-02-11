from __future__ import annotations

from django.db import models
from django.conf import settings
from typing import List
from users.models import SpaceUser

class TrainingCategory(models.Model):
    name = models.TextField()
    canvas_id = models.IntegerField(null=True, blank=True)
    user_url = models.TextField(null=True, blank=True)
    
    @property
    def name_readable(self):
        return self.name.replace("_", " ")
    
    def __str__(self):
        return self.name

class TrainingManager(models.Manager):
    def get_users_trainings(self, user: SpaceUser) -> List[Training]:
        trainings = list(self.filter(user=user).order_by("category", "-training_level").distinct("category").all())
        print(f"Getting Trainings for {user}")
        for t in trainings:
            print(t)
        return trainings
class Training(models.Model):
    class TrainingLevels(models.IntegerChoices):
        RED_DOT = 0
        GREEN_DOT = 30
        BLUE_DOT = 70
        YELLOW_DOT = 100
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trainings")
    category = models.ForeignKey(TrainingCategory, on_delete=models.PROTECT, related_name="trainings")
    training_level = models.IntegerField(choices=TrainingLevels.choices, default=TrainingLevels.RED_DOT)
    completed_on = models.DateTimeField(auto_now_add=True)
    objects = TrainingManager()
    
    @property
    def hex_color(self):
        match self.training_level:
            case Training.TrainingLevels.RED_DOT:
                return "#C33D2A"
            case Training.TrainingLevels.GREEN_DOT:
                return "#3E9955"
            case Training.TrainingLevels.BLUE_DOT:
                return "#1F70B8"
            case Training.TrainingLevels.YELLOW_DOT:
                return "#D1A300"
            case _:
                return "#FFFFFF"
    
    @property
    def icon(self):
        match self.training_level:
            case Training.TrainingLevels.RED_DOT:
                return "fa-shoe-prints"
            case Training.TrainingLevels.GREEN_DOT:
                return "fa-dumbbell"
            case Training.TrainingLevels.BLUE_DOT:
                return "fa-medal"
            case Training.TrainingLevels.YELLOW_DOT:
                return "fa-chess-king"
            case _:
                return ""
    
    def __str__(self):
        return f"{self.get_training_level_display()} in {self.category}"