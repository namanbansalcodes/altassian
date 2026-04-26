from django.urls import path

from .invite_views import (
    InviteAcceptView,
    InviteByTokenView,
    InviteDeleteView,
    InviteListCreateView,
)

urlpatterns = [
    path("invites", InviteListCreateView.as_view()),
    path("invites/<int:pk>", InviteDeleteView.as_view()),
    path("invites/by-token/<str:token>", InviteByTokenView.as_view()),
    path("invites/by-token/<str:token>/accept", InviteAcceptView.as_view()),
]
