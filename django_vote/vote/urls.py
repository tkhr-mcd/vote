from django.urls import path
from vote import views

urlpatterns = [
    path("new/", views.vote_new, name='vote_new'),
    path("<int:vote_id>", views.vote_detail, name="vote_detail"),
]