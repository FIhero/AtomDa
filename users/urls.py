from django.urls import path

from .views import UserListView, UserProfileView, UserRegistrationView

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user-register"),
    path("me/", UserProfileView.as_view(), name="user-profile"),
    path("", UserListView.as_view(), name="user-list"),
]
