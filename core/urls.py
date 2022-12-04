from django.contrib.auth.views import LoginView
from django.urls import path

from .views import views

urlpatterns = [
    path('', views.index, name='index'),
    path('qcde/', views.qcde, name='qcde'),
    path('auth/login/', LoginView.as_view(), name='login'),
]
