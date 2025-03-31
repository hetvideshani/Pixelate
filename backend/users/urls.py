from django.urls import path
from .views import signup, signin, getuserprofile, updateuserprofile, sendverificationcode, changepassword

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("signin/", signin, name="signin"),
    path("getuserprofile/", getuserprofile, name="getuserprofile"),
    path("updateuserprofile/", updateuserprofile, name="updateuserprofile"),
    path("sendverificationcode/", sendverificationcode, name="sendverificationcode"),
    path("changepassword/", changepassword, name="changepassword"),
]