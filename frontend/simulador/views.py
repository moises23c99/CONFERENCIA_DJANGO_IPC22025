from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from .forms import XMLUploadForm
from .services import procesar_configuracion_xml  # lo importarás de otro archivo
import requests
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
import xmltodict


def index(request):
    return render(request, 'simulador/index.html')

def cargar_configuracion(request):
    return render(request, 'simulador/carga_config.html')

def cargar_consumo(request):
    return render(request, 'simulador/carga_consumo.html')

def crear_datos(request):
    return render(request, 'simulador/crear_datos.html')

def cargar_configuracion(request):
    resultado = None

    if request.method == 'POST':
        form = XMLUploadForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo']
            resultado = procesar_configuracion_xml(archivo)  # lógica separada
            messages.success(request, resultado['mensaje'])
        else:
            messages.error(request, "Formulario inválido.")
    else:
        form = XMLUploadForm()

    return render(request, 'simulador/carga_config.html', {
        'form': form,
        'resultado': resultado
    })

def consultar_datos(request):
    datos = {}
    error = None

    try:
        response = requests.get('http://localhost:5000/api/consultarDatos')
        if response.status_code == 200:
            raw = response.json().get('archivoConfiguraciones', {})
            datos = normalizar_atributos(raw)  # <- aquí aplicas la función que normaliza
        else:
            error = response.json().get('mensaje', 'Error al consultar los datos.')
    except Exception as e:
        error = f"No se pudo conectar al backend: {str(e)}"

    return render(request, 'simulador/consultar_datos.html', {
        'datos': datos,
        'error': error
    })


import html

def normalizar_atributos(data):
    """
    Normaliza claves y valores:
    - '@id' → 'id_'
    - '#text' → 'text'
    - Decodifica caracteres mal representados como 'Configuraci�n'
    - Aplica recursivamente a listas y diccionarios
    """
    if isinstance(data, dict):
        nuevo = {}
        for clave, valor in data.items():
            clave_limpia = clave.replace('@', 'id_') if '@' in clave else clave.replace('#', 'text') if '#' in clave else clave
            nuevo[clave_limpia] = normalizar_atributos(valor)
        return nuevo

    elif isinstance(data, list):
        return [normalizar_atributos(i) for i in data]

    elif isinstance(data, str):
        # Paso 1: decodifica entidades HTML (&aacute; → á)
        data = html.unescape(data)
        try:
            # Paso 2: reinterpreta caracteres mal decodificados (como �)
            return data.encode('latin1').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            return data

    return data

def consultar_datos(request):
    datos = {}
    error = None

    try:
        response = requests.get('http://localhost:5000/api/consultarDatos')
        if response.status_code == 200:
            raw = response.json().get('archivoConfiguraciones', {})
            datos = normalizar_atributos(raw)
        else:
            error = response.json().get('mensaje', 'Error al consultar los datos.')
    except Exception as e:
        error = f"No se pudo conectar al backend: {str(e)}"

    return render(request, 'simulador/consultar_datos.html', {
        'datos': datos,
        'error': error
    })
