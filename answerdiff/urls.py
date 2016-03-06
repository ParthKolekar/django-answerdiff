from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    url(r'^problems/$', views.ListProblems.as_view()),
    url(r'^level/(?P<level>[0-9]+)/$', views.LevelDetails.as_view()),
    url(r'^problems/(?P<question_level>[0-9]+)/(?P<question_number>[0-9]+)/$', views.QuestionDetails.as_view()),
    url(r'^scoreboard/$',views.Scoreboard.as_view()),
    url(r'^comment/(?P<question_level>[0-9]+)/(?P<question_number>[0-9]+)/$',views.CommentDetails.as_view()),
    url(r'^mysubmissions/$',views.ListSubmissions.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
