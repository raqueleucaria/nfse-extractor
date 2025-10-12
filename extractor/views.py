from django.http import JsonResponse
from django.shortcuts import render

def index(request ):
    """View principal - Hello World"""
    return render(request, 'extractor/index.html')

def hello_api(request):
    """API Hello World - retorna JSON"""
    return JsonResponse({
        'message': 'Hello World - NFSe Extractor API',
        'status': 'online'
    })
