from django.urls import path
from .views import get_courses

urlpatterns = [
    path("get/", get_courses, name="get courses"),
]
