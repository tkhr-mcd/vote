from django.urls import path, re_path
from .views import indexfunc, areafunc,constituencyfunc, vote_new, vote_detail, testfunc, candidatefunc

app_name = 'vote'
urlpatterns = [
    path("vote/", indexfunc, name='index'),
    path("area/", areafunc, name = 'area'),
    path("test/", testfunc, name = 'test'),
    path("constituency/<str:prefecture>", constituencyfunc, name = 'constituency'),
    path("constituency/<str:prefecture>/<int:constituency>", candidatefunc, name = 'candidate'),
    path("new/", vote_new, name='vote_new'),
    path("<int:vote_id>", vote_detail, name="vote_detail"),
]