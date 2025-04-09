import os
import xmltodict

def leer_xml(ruta, estructura_vacia):
    """
    Lee un archivo XML y lo convierte en un diccionario.
    Si el archivo no existe o está vacío, lo crea con una estructura vacía.
    """
    import os
    import xmltodict

    if not os.path.exists(ruta) or os.path.getsize(ruta) == 0:
        # Crear el archivo con la estructura vacía si no existe
        with open(ruta, "w", encoding="utf-8") as file:
            file.write(estructura_vacia)
        return xmltodict.parse(estructura_vacia)

    # Leer el archivo con codificación UTF-8
    with open(ruta, "r", encoding="utf-8") as file:
        contenido = file.read().strip()
        if not contenido:  # Si el archivo está vacío
            with open(ruta, "w", encoding="utf-8") as file:
                file.write(estructura_vacia)
            return xmltodict.parse(estructura_vacia)
        return xmltodict.parse(contenido)
    

def escribir_xml(ruta, data):
    """
    Convierte un diccionario a XML y lo guarda en un archivo.
    """
    import xmltodict

    try:
        with open(ruta, "w", encoding="utf-8") as file:
            xml_content = xmltodict.unparse(data, pretty=True)
            file.write(xml_content)
    except Exception as e:
        print(f"Error al escribir el archivo XML: {e}")