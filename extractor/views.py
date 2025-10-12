from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from .data_extractor import extract_nfse_data

def index(request ):
    """View principal - Hello World"""
    return render(request, 'extractor/index.html')

def hello_api(request):
    """API Hello World - retorna JSON"""
    return JsonResponse({
        'message': 'Hello World - NFSe Extractor API',
        'status': 'online'
    })


@csrf_exempt
def extract_api(request):
    """API para extrair dados de NFSe"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    if 'file' not in request.FILES:
        return JsonResponse({
            'error': 'Nenhum arquivo enviado. Envie um arquivo no campo "file".'
        }, status=400)
    
    try:
        uploaded_file = request.FILES['file']
        
        file_name = default_storage.save(uploaded_file.name, ContentFile(uploaded_file.read()))
        file_path = default_storage.path(file_name)
        
        result = extract_nfse_data(file_path)
        default_storage.delete(file_name)
        
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})   
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)