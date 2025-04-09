from flask import Blueprint, request, jsonify
from models import Cliente  # Importar la clase Cliente desde models.py
from utils import leer_xml, escribir_xml
import os  # Importar el módulo os para manejar rutas de archivos
import xml.etree.ElementTree as ET
import xmltodict

api = Blueprint('api', __name__)

import os

# Define la ruta absoluta al archivo XML en la carpeta database a nivel del proyecto
DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "archivoConfiguraciones.xml")
@api.route('/api/configuracion', methods=['POST'])
def cargar_configuracion():
    if 'archivo' not in request.files:
        return jsonify({"error": "No se proporcionó un archivo."}), 400

    archivo = request.files['archivo']

    if archivo.filename == '':
        return jsonify({"error": "El archivo está vacío."}), 400

    try:
        # Leer y parsear el XML en memoria
        tree = ET.parse(archivo)
        root = tree.getroot()

        # Contar elementos relevantes
        recursos = len(root.findall('.//listaRecursos/recurso'))
        categorias = len(root.findall('.//listaCategorias/categoria'))
        configuraciones = len(root.findall('.//listaCategorias/categoria/listaConfiguraciones/configuracion'))
        clientes = len(root.findall('.//listaClientes/cliente'))
        instancias = len(root.findall('.//listaClientes/cliente/listaInstancias/instancia'))

        # Guardar el archivo si todo es válido
        ruta_archivo = os.path.join('database', 'archivoConfiguraciones.xml')
        os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
        tree.write(ruta_archivo)

        return jsonify({
            "recursos": recursos,
            "categorias": categorias,
            "configuraciones": configuraciones,
            "clientes": clientes,
            "instancias": instancias,
            "mensaje": "Archivo procesado exitosamente."
        }), 200

    except ET.ParseError:
        return jsonify({"error": "El archivo no es un XML válido."}), 400
    except Exception as e:
        return jsonify({"error": f"Ocurrió un error inesperado: {str(e)}"}), 500


@api.route('/api/consultarDatos', methods=['GET'])
def consultar_datos():
    """
    Consulta los datos del archivo archivoConfiguraciones.xml y los devuelve en formato JSON.
    """
    # Leer el archivo XML
    estructura_vacia = '<?xml version="1.0"?><configuracion></configuracion>'
    data = leer_xml(DATABASE_PATH, estructura_vacia)

    # Verificar si el archivo tiene datos
    if not data or data == {"configuracion": None}:
        return jsonify({"mensaje": "No hay datos disponibles en el archivo de configuración."}), 404
    
    # Función para remover '@' de los atributos del JSON
    def clean_data(data):
        if isinstance(data, dict):
            # Recorre el diccionario y limpia las claves que contienen '@'
            return {key.lstrip('@'): clean_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            # Si el valor es una lista, recursivamente limpia los elementos
            return [clean_data(item) for item in data]
        else:
            return data

    # Limpiar los datos antes de devolverlos
    cleaned_data = clean_data(data)

    # Devolver los datos en formato JSON
    return jsonify(cleaned_data), 200

@api.route('/api/crearRecurso', methods=['POST'])
def crear_recurso():
    """
    Crea un nuevo recurso y lo agrega a <listaRecursos> en archivoConfiguraciones.xml.
    """
    # Obtener los datos del recurso desde la solicitud
    datos_recurso = request.json

    # Validar los campos requeridos
    campos_requeridos = ["id_recurso", "nombre", "abreviatura", "metrica", "tipo", "valor_hora"]
    error = validar_campos_requeridos(datos_recurso, campos_requeridos)
    if error:
        return jsonify({"error": error}), 400

    # Crear el nuevo recurso
    nuevo_recurso = {
        "@id": datos_recurso["id_recurso"],
        "nombre": datos_recurso["nombre"],
        "abreviatura": datos_recurso["abreviatura"],
        "metrica": datos_recurso["metrica"],
        "tipo": datos_recurso["tipo"],
        "valorXhora": datos_recurso["valor_hora"]
    }

    # Leer el archivo XML
    estructura_vacia = '<?xml version="1.0"?><archivoConfiguraciones><listaRecursos></listaRecursos></archivoConfiguraciones>'
    data = leer_xml(DATABASE_PATH, estructura_vacia)

    # Asegurarse de que <listaRecursos> exista
    if "listaRecursos" not in data["archivoConfiguraciones"]:
        data["archivoConfiguraciones"]["listaRecursos"] = {"recurso": []}

    # Normalizar <recurso> como lista si es necesario
    if isinstance(data["archivoConfiguraciones"]["listaRecursos"].get("recurso"), dict):
        data["archivoConfiguraciones"]["listaRecursos"]["recurso"] = [data["archivoConfiguraciones"]["listaRecursos"]["recurso"]]

    # Agregar el nuevo recurso a la lista
    data["archivoConfiguraciones"]["listaRecursos"]["recurso"].append(nuevo_recurso)

    # Guardar los cambios en el archivo XML
    escribir_xml(DATABASE_PATH, data)

    return jsonify({"mensaje": "Recurso creado exitosamente"}), 201

def validar_campos_requeridos(datos, campos_requeridos):
    """
    Valida que los campos requeridos estén presentes en los datos recibidos.
    """
    for campo in campos_requeridos:
        if campo not in datos:
            return f"Falta el campo requerido: {campo}"
    return None

@api.route('/api/crearCategoria', methods=['POST'])
def crear_categoria():
    """
    Crea una nueva categoría y la agrega a <listaCategorias> en archivoConfiguraciones.xml.
    """
    # Obtener los datos de la categoría desde la solicitud
    datos_categoria = request.json

    # Validar que los datos necesarios estén presentes
    try:
        nueva_categoria = {
            "@id": datos_categoria["id_categoria"],
            "nombre": datos_categoria["nombre"],
            "descripcion": datos_categoria["descripcion"],
            "cargaTrabajo": datos_categoria["cargaTrabajo"],  # Puede ser una lista o un string
            "listaConfiguraciones": {}  # Inicializar como vacío
        }
    except KeyError as e:
        return jsonify({"error": f"Falta el campo requerido: {str(e)}"}), 400

    # Leer el archivo XML
    estructura_vacia = '<?xml version="1.0" encoding="UTF-8"?><archivoConfiguraciones><listaCategorias></listaCategorias></archivoConfiguraciones>'
    data = leer_xml(DATABASE_PATH, estructura_vacia)

    # Asegurarse de que <listaCategorias> exista
    if "listaCategorias" not in data["archivoConfiguraciones"] or data["archivoConfiguraciones"]["listaCategorias"] is None:
        data["archivoConfiguraciones"]["listaCategorias"] = {"categoria": []}

    # Normalizar <categoria> como lista si es necesario
    if isinstance(data["archivoConfiguraciones"]["listaCategorias"].get("categoria"), dict):
        data["archivoConfiguraciones"]["listaCategorias"]["categoria"] = [data["archivoConfiguraciones"]["listaCategorias"]["categoria"]]

    # Agregar la nueva categoría a la lista
    data["archivoConfiguraciones"]["listaCategorias"]["categoria"].append(nueva_categoria)

    # Guardar los cambios en el archivo XML
    escribir_xml(DATABASE_PATH, data)

    return jsonify({"mensaje": "Categoría creada exitosamente"}), 201

@api.route('/api/crearConfiguracion', methods=['POST'])
def crear_configuracion():
    """
    Crea una nueva configuración y la agrega a <listaConfiguraciones> dentro de la categoría correspondiente en archivoConfiguraciones.xml.
    """
    # Obtener los datos de la configuración desde la solicitud
    datos_configuracion = request.json

    # Validar que los datos necesarios estén presentes
    try:
        id_categoria = datos_configuracion["id_categoria"]  # ID de la categoría a la que pertenece la configuración
        nueva_configuracion = {
            "@id": datos_configuracion["id_configuracion"],
            "nombre": datos_configuracion["nombre"],
            "descripcion": datos_configuracion["descripcion"],
            "parametros": datos_configuracion.get("parametros", {})  # Opcional, puede ser un diccionario vacío
        }
    except KeyError as e:
        return jsonify({"error": f"Falta el campo requerido: {str(e)}"}), 400

    # Leer el archivo XML
    estructura_vacia = '<?xml version="1.0"?><archivoConfiguraciones><listaCategorias></listaCategorias></archivoConfiguraciones>'
    data = leer_xml(DATABASE_PATH, estructura_vacia)

    # Asegurarse de que <listaCategorias> exista
    if "listaCategorias" not in data["archivoConfiguraciones"] or data["archivoConfiguraciones"]["listaCategorias"] is None:
        return jsonify({"error": "No existen categorías en el archivo de configuración."}), 404

    # Normalizar <categoria> como lista si es necesario
    if isinstance(data["archivoConfiguraciones"]["listaCategorias"].get("categoria"), dict):
        data["archivoConfiguraciones"]["listaCategorias"]["categoria"] = [data["archivoConfiguraciones"]["listaCategorias"]["categoria"]]

    # Buscar la categoría correspondiente por ID
    categoria_encontrada = None
    for categoria in data["archivoConfiguraciones"]["listaCategorias"]["categoria"]:
        if categoria["@id"] == id_categoria:
            categoria_encontrada = categoria
            break

    if not categoria_encontrada:
        return jsonify({"error": f"No se encontró la categoría con ID: {id_categoria}"}), 404

    # Asegurarse de que <listaConfiguraciones> exista dentro de la categoría
    if "listaConfiguraciones" not in categoria_encontrada or categoria_encontrada["listaConfiguraciones"] is None:
        categoria_encontrada["listaConfiguraciones"] = {"configuracion": []}

    # Normalizar <configuracion> como lista si es necesario
    if isinstance(categoria_encontrada["listaConfiguraciones"].get("configuracion"), dict):
        categoria_encontrada["listaConfiguraciones"]["configuracion"] = [categoria_encontrada["listaConfiguraciones"]["configuracion"]]

    # Agregar la nueva configuración a la lista de configuraciones de la categoría
    categoria_encontrada["listaConfiguraciones"]["configuracion"].append(nueva_configuracion)

    # Guardar los cambios en el archivo XML
    escribir_xml(DATABASE_PATH, data)

    return jsonify({"mensaje": "Configuración creada exitosamente"}), 201

@api.route('/api/crearCliente', methods=['POST'])
def crear_cliente():
    """
    Crea un nuevo cliente y lo agrega a <listaClientes> en archivoConfiguraciones.xml.
    """
    # Obtener los datos del cliente desde la solicitud
    datos_cliente = request.json

    # Validar que los datos necesarios estén presentes
    try:
        nuevo_cliente = {
            "@id": datos_cliente["id_cliente"],
            "nombre": datos_cliente["nombre"],
            "email": datos_cliente["email"],
            "telefono": datos_cliente.get("telefono", ""),  # Opcional
            "direccion": datos_cliente.get("direccion", "")  # Opcional
        }
    except KeyError as e:
        return jsonify({"error": f"Falta el campo requerido: {str(e)}"}), 400

    # Leer el archivo XML
    estructura_vacia = '<?xml version="1.0"?><archivoConfiguraciones><listaClientes></listaClientes></archivoConfiguraciones>'
    data = leer_xml(DATABASE_PATH, estructura_vacia)

    # Asegurarse de que <listaClientes> exista
    if "listaClientes" not in data["archivoConfiguraciones"] or data["archivoConfiguraciones"]["listaClientes"] is None:
        data["archivoConfiguraciones"]["listaClientes"] = {"cliente": []}

    # Normalizar <cliente> como lista si es necesario
    if isinstance(data["archivoConfiguraciones"]["listaClientes"].get("cliente"), dict):
        data["archivoConfiguraciones"]["listaClientes"]["cliente"] = [data["archivoConfiguraciones"]["listaClientes"]["cliente"]]

    # Agregar el nuevo cliente a la lista
    data["archivoConfiguraciones"]["listaClientes"]["cliente"].append(nuevo_cliente)

    # Guardar los cambios en el archivo XML
    escribir_xml(DATABASE_PATH, data)

    return jsonify({"mensaje": "Cliente creado exitosamente"}), 201

@api.route('/api/crearInstancia', methods=['POST'])
def crear_instancia():
    """
    Crea una nueva instancia y la agrega a <listaInstancias> dentro del cliente correspondiente en archivoConfiguraciones.xml.
    """
    # Obtener los datos de la instancia desde la solicitud
    datos_instancia = request.json

    # Validar que los datos necesarios estén presentes
    try:
        id_cliente = datos_instancia["id_cliente"]  # ID o NIT del cliente al que pertenece la instancia
        nueva_instancia = {
            "@id": datos_instancia["id_instancia"],
            "idConfiguracion": datos_instancia["id_configuracion"],
            "nombre": datos_instancia["nombre"],
            "fechaInicio": datos_instancia["fecha_inicio"],
            "estado": datos_instancia["estado"],
            "fechaFinal": datos_instancia.get("fecha_final", "")  # Opcional
        }
    except KeyError as e:
        return jsonify({"error": f"Falta el campo requerido: {str(e)}"}), 400

    # Leer el archivo XML
    estructura_vacia = '<?xml version="1.0"?><archivoConfiguraciones><listaClientes></listaClientes></archivoConfiguraciones>'
    data = leer_xml(DATABASE_PATH, estructura_vacia)

    # Asegurarse de que <listaClientes> exista
    if "listaClientes" not in data["archivoConfiguraciones"] or data["archivoConfiguraciones"]["listaClientes"] is None:
        return jsonify({"error": "No existen clientes en el archivo de configuración."}), 404

    # Normalizar <cliente> como lista si es necesario
    if isinstance(data["archivoConfiguraciones"]["listaClientes"].get("cliente"), dict):
        data["archivoConfiguraciones"]["listaClientes"]["cliente"] = [data["archivoConfiguraciones"]["listaClientes"]["cliente"]]

    # Buscar el cliente correspondiente por NIT
    cliente_encontrado = None
    for cliente in data["archivoConfiguraciones"]["listaClientes"]["cliente"]:
        if cliente.get("@nit") == id_cliente or cliente.get("@id") == id_cliente:  # Buscar por NIT o ID
            cliente_encontrado = cliente
            break


    if not cliente_encontrado:
        return jsonify({"error": f"No se encontró el cliente con NIT: {id_cliente}"}), 404

    # Asegurarse de que <listaInstancias> exista dentro del cliente
    if "listaInstancias" not in cliente_encontrado or cliente_encontrado["listaInstancias"] is None:
        cliente_encontrado["listaInstancias"] = {"instancia": []}

    # Normalizar <instancia> como lista si es necesario
    if isinstance(cliente_encontrado["listaInstancias"].get("instancia"), dict):
        cliente_encontrado["listaInstancias"]["instancia"] = [cliente_encontrado["listaInstancias"]["instancia"]]

    # Agregar la nueva instancia a la lista de instancias del cliente
    cliente_encontrado["listaInstancias"]["instancia"].append(nueva_instancia)

    # Guardar los cambios en el archivo XML
    escribir_xml(DATABASE_PATH, data)

    return jsonify({"mensaje": "Instancia creada exitosamente"}), 201

@api.route('/api/generaFactura', methods=['POST'])
def genera_factura():
    """
    Genera una factura basada en los datos de archivoConfiguraciones.xml y guarda la factura en facturas.xml.
    """
    # Obtener los datos necesarios desde la solicitud
    datos_factura = request.json

    # Validar que los datos necesarios estén presentes
    try:
        nit_cliente = datos_factura["nit_cliente"]  # NIT del cliente
        id_instancia = datos_factura.get("id_instancia", None)  # Opcional: ID de la instancia
        tarifa_por_hora = float(datos_factura["tarifa_por_hora"])  # Tarifa por hora de consumo
    except KeyError as e:
        return jsonify({"error": f"Falta el campo requerido: {str(e)}"}), 400

    # Leer el archivo XML de configuraciones
    estructura_configuraciones = '<?xml version="1.0"?><archivoConfiguraciones><listaClientes></listaClientes></archivoConfiguraciones>'
    configuraciones = leer_xml("c:\\Users\\Moises Conde\\Documents\\Conferencia\\backend\\database\\archivoConfiguraciones.xml", estructura_configuraciones)

    # Asegurarse de que <listaClientes> exista en archivoConfiguraciones.xml
    if "listaClientes" not in configuraciones["archivoConfiguraciones"] or configuraciones["archivoConfiguraciones"]["listaClientes"] is None:
        return jsonify({"error": "No existen clientes en el archivo de configuraciones."}), 404

    # Normalizar <cliente> como lista si es necesario
    if isinstance(configuraciones["archivoConfiguraciones"]["listaClientes"].get("cliente"), dict):
        configuraciones["archivoConfiguraciones"]["listaClientes"]["cliente"] = [configuraciones["archivoConfiguraciones"]["listaClientes"]["cliente"]]

    # Buscar el cliente correspondiente por NIT
    cliente_encontrado = None
    for cliente in configuraciones["archivoConfiguraciones"]["listaClientes"]["cliente"]:
        if cliente.get("@nit") == nit_cliente:
            cliente_encontrado = cliente
            break

    if not cliente_encontrado:
        return jsonify({"error": f"No se encontró el cliente con NIT: {nit_cliente}"}), 404

    # Asegurarse de que <listaInstancias> exista dentro del cliente
    if "listaInstancias" not in cliente_encontrado or cliente_encontrado["listaInstancias"] is None:
        return jsonify({"error": f"No se encontraron instancias para el cliente con NIT: {nit_cliente}"}), 404

    # Normalizar <instancia> como lista si es necesario
    if isinstance(cliente_encontrado["listaInstancias"].get("instancia"), dict):
        cliente_encontrado["listaInstancias"]["instancia"] = [cliente_encontrado["listaInstancias"]["instancia"]]

    # Buscar la instancia específica (si se proporciona)
    instancia_encontrada = None
    if id_instancia:
        for instancia in cliente_encontrado["listaInstancias"]["instancia"]:
            if instancia.get("@id") == id_instancia:
                instancia_encontrada = instancia
                break

        if not instancia_encontrada:
            return jsonify({"error": f"No se encontró la instancia con ID: {id_instancia} para el cliente con NIT: {nit_cliente}"}), 404

    # Calcular el total de la factura
    tiempo_consumido = float(instancia_encontrada.get("tiempo", 0))  # Tiempo consumido en horas
    total_factura = tiempo_consumido * tarifa_por_hora

    # Crear la factura
    nueva_factura = {
        "@nitCliente": nit_cliente,
        "@idInstancia": id_instancia,
        "total": total_factura,
        "fechaHora": datos_factura.get("fecha_hora", "2025-03-31T10:00:00")  # Fecha y hora opcional
    }

    # Leer el archivo XML de facturas
    estructura_facturas = '<?xml version="1.0"?><listadoConsumos></listadoConsumos>'
    facturas = leer_xml("c:\\Users\\Moises Conde\\Documents\\Conferencia\\backend\\database\\facturas.xml", estructura_facturas)

    # Asegurarse de que <listadoConsumos> exista
    if "listadoConsumos" not in facturas or facturas["listadoConsumos"] is None:
        facturas["listadoConsumos"] = {"consumo": []}

    # Normalizar <consumo> como lista si es necesario
    if isinstance(facturas["listadoConsumos"].get("consumo"), dict):
        facturas["listadoConsumos"]["consumo"] = [facturas["listadoConsumos"]["consumo"]]

    # Agregar la nueva factura al listado de consumos
    facturas["listadoConsumos"]["consumo"].append(nueva_factura)

    # Guardar los cambios en el archivo XML de facturas
    escribir_xml("c:\\Users\\Moises Conde\\Documents\\Conferencia\\backend\\database\\facturas.xml", facturas)

    return jsonify({"mensaje": "Factura generada y guardada exitosamente.", "factura": nueva_factura}), 201