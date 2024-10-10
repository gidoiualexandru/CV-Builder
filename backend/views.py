from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import BaseTemplate, GeneratedResume
from .forms import BaseTemplateForm, JobDescriptionForm
from django.http import HttpResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

import os
from django.conf import settings
from docx import Document
from PyPDF2 import PdfReader, PdfWriter
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import io

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

def generate_resume(base_template, job_description):
    # Analyze job description
    tokens = word_tokenize(job_description.lower())
    stop_words = set(stopwords.words('english'))
    keywords = [word for word in tokens if word.isalnum() and word not in stop_words]
    
    # Read and modify base template
    file_extension = os.path.splitext(base_template.file.name)[1].lower()
    
    if file_extension == '.docx':
        return modify_docx(base_template.file.path, keywords)
    elif file_extension == '.pdf':
        return modify_pdf(base_template.file.path, keywords)
    else:
        raise ValueError("Unsupported file format")

def modify_docx(file_path, keywords):
    doc = Document(file_path)
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            for keyword in keywords:
                if keyword in run.text.lower():
                    run.bold = True
    
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    return output

def modify_pdf(file_path, keywords):
    reader = PdfReader(file_path)
    writer = PdfWriter()

    for page in reader.pages:
        text = page.extract_text()
        for keyword in keywords:
            if keyword in text.lower():
                # Here we're just copying the page as-is
                # In a real implementation, you'd modify the page content
                writer.add_page(page)
                break
        else:
            writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output

@login_required
def upload_base_template(request):
    if request.method == 'POST':
        form = BaseTemplateForm(request.POST, request.FILES)
        if form.is_valid():
            template = form.save(commit=False)
            template.user = request.user
            template.save()
            return redirect('cv_template')
    else:
        form = BaseTemplateForm()
    return render(request, 'cv_template.html', {'form': form})

@login_required
def input_job_description(request):
    if request.method == 'POST':
        form = JobDescriptionForm(request.POST)
        if form.is_valid():
            job_description = form.cleaned_data['job_description']
            base_template = BaseTemplate.objects.filter(user=request.user).first()
            if base_template:
                generated_resume = GeneratedResume.objects.create(
                    user=request.user,
                    base_template=base_template,
                    job_description=job_description
                )
                # Generate PDF (placeholder implementation)
                buffer = io.BytesIO()
                p = canvas.Canvas(buffer, pagesize=letter)
                p.drawString(100, 750, "Custom Resume")
                p.drawString(100, 700, "Job Description:")
                p.drawString(100, 680, job_description[:50] + "...")
                p.showPage()
                p.save()
                buffer.seek(0)
                return HttpResponse(buffer, content_type='application/pdf')
            else:
                return HttpResponse("Please upload a base template first.")
    else:
        form = JobDescriptionForm()
    return render(request, 'input_job.html', {'form': form})