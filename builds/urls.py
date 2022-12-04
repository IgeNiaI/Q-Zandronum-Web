from django.urls import path

from .views import views

urlpatterns = [
    path('upload/qz/', views.chunked_upload_form, name='chunked_upload'),
    path('upload/qcde/', views.qcde_chunked_upload, name='qcde_chunked_upload'),
    path('upload/complete/', views.chunked_upload_complete, name='api_chunked_upload_complete'),
    path('upload/process/', views.chunked_upload_process, name='api_chunked_upload'),

]
