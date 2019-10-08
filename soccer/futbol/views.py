from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseNotFound,HttpResponseRedirect
from django.urls import reverse
from django.core.files.storage import FileSystemStorage

def index(request):
    return render(request,'futbol/index.html')

def inicio(request):
    return render(request,'futbol/home.html')

def actualizar(request):
    return render(request,'futbol/actualizar.html')

def simple_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        return render(request, 'futbol/success.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return redirect('futbolmod:actualizar')


def add_team(request):
    pass

def add_league(request):
    pass
