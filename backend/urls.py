from django.urls import path
from . import views

urlpatterns = [
    path('upload-template/', views.upload_base_template, name='cv_template'),
    path('input-job/', views.input_job_description, name='input_job'),
]