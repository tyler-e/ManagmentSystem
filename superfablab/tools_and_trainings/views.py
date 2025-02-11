from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from .models import Training, TrainingCategory
from django.utils.timezone import now, localtime
from visit_tracking.models import Visit
from users.models import SpaceUser
from django.contrib.auth.decorators import permission_required, user_passes_test
from django.contrib.auth import get_user_model



def staff_required(view_func):
    return user_passes_test(lambda u: u.space_level >= get_user_model().SpaceLevel.KEYHOLDER)(view_func)


@staff_required
def create_training(request):
    if request.POST:
        print(f"POST {request.POST}")
        user = SpaceUser.objects.get(niner_id=request.POST['user'])
        category = TrainingCategory.objects.get(id=request.POST['category'])
        training = Training.objects.create(user=user, category=category, training_level=request.POST['level'])

        return redirect("home")
    
    
    context = {
        "current_visits": list(Visit.objects.get_signed_in_users()),
        "available_trainings": list(TrainingCategory.objects.all()),
        "training_levels": Training.TrainingLevels.choices
    }
    
    return render(request, "training_form.html", context)