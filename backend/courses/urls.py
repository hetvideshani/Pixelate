from django.urls import path
from .views import get_courses, add_courses, get_by_id, update_course, delete_course

urlpatterns = [
    path("get_all/", get_courses, name="get courses"),
    path("<uuid:user_id>/add/", add_courses, name="add course"),
    path("<uuid:course_id>/", get_by_id, name="get course by id"),
    path("<uuid:user_id>/<uuid:course_id>/update", update_course, name="update course"),
    path("<uuid:user_id>/<uuid:course_id>/delete", delete_course, name="delete course"),
]
