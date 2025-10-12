from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
import tempfile
import os
from .data_extractor import extract_nfse_data, ExtractorError

def index(request):
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
        return JsonResponse({'error': 'Nenhum arquivo enviado. Envie um arquivo no campo "file".'}, status=400)
    
    temp_file_path = None
    
    try:
        uploaded_file = request.FILES['file']
        
        file_extension = Path(uploaded_file.name).suffix.lower()
        if file_extension == '.pdf':
            file_type = 'pdf'
        elif file_extension in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif']:
            file_type = 'image'
        else:
            return JsonResponse({'error': f'Tipo de arquivo não suportado: {file_extension}'}, status=400)
        
        temp_dir = Path('temp')
        temp_dir.mkdir(exist_ok=True)
        
        with tempfile.NamedTemporaryFile(
            dir=temp_dir,
            suffix=file_extension,
            prefix=f"{Path(uploaded_file.name).stem}_",
            delete=False
        ) as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        result = extract_nfse_data(temp_file_path, file_type)
        
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
        
    except ExtractorError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Erro interno: {str(e)}'}, status=500)
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass