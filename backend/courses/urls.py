from django.urls import path
from .views import get_courses, add_courses, get_by_id

urlpatterns = [
    path("get_all/", get_courses, name="get courses"),
    path("<uuid:user_id>/add/", add_courses, name="add course"),
    path("<uuid:course_id>/", get_by_id, name="get course by id"),
    
]
