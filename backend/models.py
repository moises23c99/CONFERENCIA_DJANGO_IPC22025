class Recurso:
    def __init__(self, id_recurso, nombre, abreviatura, metrica, tipo, valor_hora):
        self.id_recurso = id_recurso
        self.nombre = nombre
        self.abreviatura = abreviatura
        self.metrica = metrica
        self.tipo = tipo
        self.valor_hora = valor_hora

class Categoria:
    def __init__(self, id_categoria, nombre, descripcion,cargaTrabajo, configuracion):
        self.id_categoria = id_categoria
        self.nombre = nombre
        self.descripcion = descripcion
        self.cargaTrabajo = cargaTrabajo  
        self.configuraciones = configuracion # lista de configuraciones

class Configuracion:
    def __init__(self, id_config, nombre, descripcion, recursos):
        self.id_config = id_config
        self.nombre = nombre
        self.descripcion = descripcion
        self.recursos = recursos  # Lista de recursos
        
class Instancia:
    def __init__(self, id_instancia, nombre, fechaInicio, estado, fechaFinal):  
        self.id_instancia = id_instancia
        self.nombre = nombre
        self.fechaInicio = fechaInicio
        self.estado = estado
        self.fechaFinal = fechaFinal 
    
class Cliente:
    def __init__(self, nit, nombre, usuario, clave, direccion, correo):
        self.nit = nit
        self.nombre = nombre
        self.usuario = usuario
        self.clave = clave
        self.direccion = direccion
        self.correo = correo



