from django.contrib.auth.views import LoginView
from django.urls import path, re_path
from django.views.generic import RedirectView

from .views import views

urlpatterns = [
    path('', views.switch_view, name='index'),
    path('qcde/', views.qcde, name='qcde'),
    path('guides/installation_on_linux', views.guide, name='guides'),
    path('auth/login/', LoginView.as_view(), name='login'),
    re_path('(?:en|ru)/', RedirectView.as_view(pattern_name='index', permanent=True),),
]
