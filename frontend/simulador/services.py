import requests
import xml.etree.ElementTree as ET
from django.core.exceptions import ValidationError

def procesar_configuracion_xml(archivo):
    try:
        # Validar XML localmente
        tree = ET.parse(archivo)
        root = tree.getroot()

        if root.tag != "archivoConfiguraciones":
            raise ValidationError("El archivo XML no tiene la estructura esperada.")

        # Enviar el archivo al backend
        archivo.seek(0)
        response = requests.post(
            'http://localhost:5000/api/configuracion',
            files={'archivo': archivo}
        )

        if response.status_code != 200:
            return {
                'mensaje': f'Error al comunicarse con el backend (código {response.status_code})'
            }

        data = response.json()

        # Crear el diccionario para retornar al template
        resultado = {
            'mensaje': data.get('mensaje', 'Archivo procesado.'),
            'recursos': data.get('recursos', 0),
            'categorias': data.get('categorias', 0),
            'configuraciones': data.get('configuraciones', 0),
            'clientes_creados': data.get('clientes', 0),
            'instancias_creadas': data.get('instancias', 0)
        }

        return resultado

    except ET.ParseError:
        return {
            'mensaje': 'Error: El archivo no contiene XML válido.'
        }

    except Exception as e:
        return {
            'mensaje': f'Error inesperado: {str(e)}'
        }
