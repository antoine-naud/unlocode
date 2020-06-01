from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.UnlocodeList.as_view()),
    re_path('^name/(?P<namewodiacritics>\D+)/$', views.UnlocodeNameRetrieve.as_view()),
    re_path('^code/(?P<locode>\D+)/$', views.UnlocodeCodeRetrieve.as_view())
]
