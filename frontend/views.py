from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from backend.forms import BaseTemplateForm, JobDescriptionForm
from backend.models import BaseTemplate, GeneratedResume
from django.http import HttpResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from backend.views import generate_resume
from django.core.files.base import ContentFile
import os

def logout_view(request):
    logout(request)
    return redirect('login')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('cv_template')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

@login_required
def cv_template_view(request):
    base_template = BaseTemplate.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        form = BaseTemplateForm(request.POST, request.FILES, instance=base_template)
        if form.is_valid():
            if base_template:
                base_template.file.delete()  # Delete old file
            template = form.save(commit=False)
            template.user = request.user
            template.save()
            return redirect('cv_template')
    else:
        form = BaseTemplateForm(instance=base_template)
    
    return render(request, 'cv_template.html', {'form': form, 'base_template': base_template})

@login_required
def view_base_template(request):
    base_template = get_object_or_404(BaseTemplate, user=request.user)
    return redirect(base_template.file.url)

@login_required
@login_required
def input_job_view(request):
    if request.method == 'POST':
        form = JobDescriptionForm(request.POST)
        if form.is_valid():
            job_description = form.cleaned_data['job_description']
            base_template = BaseTemplate.objects.filter(user=request.user).first()
            if base_template:
                try:
                    generated_file = generate_resume(base_template, job_description)
                    
                    generated_resume = GeneratedResume.objects.create(
                        user=request.user,
                        base_template=base_template,
                        job_description=job_description
                    )
                    
                    file_extension = os.path.splitext(base_template.file.name)[1].lower()
                    generated_resume.generated_file.save(
                        f'resume_{generated_resume.id}{file_extension}',
                        ContentFile(generated_file.getvalue())
                    )
                    
                    return redirect('view_generated_resume', resume_id=generated_resume.id)
                except Exception as e:
                    return HttpResponse(f"Error generating resume: {str(e)}")
            else:
                return HttpResponse("Please upload a base template first.")
    else:
        form = JobDescriptionForm()
    
    generated_resumes = GeneratedResume.objects.filter(user=request.user)
    return render(request, 'input_job.html', {'form': form, 'generated_resumes': generated_resumes})

@login_required
def view_generated_resume(request, resume_id):
    resume = GeneratedResume.objects.get(id=resume_id, user=request.user)
    return render(request, 'view_generated_resume.html', {'resume': resume})