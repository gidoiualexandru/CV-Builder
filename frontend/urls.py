from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cv-template/', views.cv_template_view, name='cv_template'),
    path('input-job/', views.input_job_view, name='input_job'),
    path('view-resume/<int:resume_id>/', views.view_generated_resume, name='view_generated_resume'),
    path('view-base-template/', views.view_base_template, name='view_base_template'),
]