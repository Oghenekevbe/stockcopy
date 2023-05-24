from django.shortcuts import render
from .mongo_setup import mongodb

# Create your views here.

def index(request):
    return render(request,'index.html')