from django.urls import path, re_path
from .views import indexfunc, areafunc,constituencyfunc, vote_new, vote_detail, candidatefunc, contactfunc, confirmfunc, completefunc, resultfunc, summaryfunc

app_name = 'vote'
urlpatterns = [
    path("", indexfunc, name='index'),
    path("contact/", contactfunc, name = 'contact'),
    path("confirm/", confirmfunc, name = 'confirm'),
    path("complete/", completefunc, name = 'complete'),
    path("result/", resultfunc, name = 'result'),
    path("area/", areafunc, name = 'area'),
    path("summary/<str:person_name>", summaryfunc, name = 'summary'),
    path("constituency/<str:prefecture>", constituencyfunc, name = 'constituency'),
    path("constituency/<str:prefecture>/<int:constituency>", candidatefunc, name = 'candidate'),
    path("new/", vote_new, name='vote_new'),
    path("<int:vote_id>", vote_detail, name="vote_detail"),
]
