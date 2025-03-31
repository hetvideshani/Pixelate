from django.urls import path
from .views import create_feedback

urlpatterns = [
    path("<uuid:user_id>/<uuid:course_id>/add/", create_feedback, name="create feedback"),
]
