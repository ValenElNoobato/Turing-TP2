from enum import Enum

class Estado():
    def __init__(self, nombre: str):
        self.nombre = nombre

    def __str__(self):
        return self.nombre

    def __eq__(self, other):
        if not isinstance(other, Estado):
            return NotImplemented
        return self.nombre == other.nombre

class Desplazamiento(Enum):
    L = "L"
    R = "R"
    Simbolo = ""
    

class Transicion():
    def __init__(self, estadoInicial: Estado, estadoDestino: Estado, elemento: str, desplazamiento: Desplazamiento):        
        self.estadoInicial = estadoInicial
        self.estadoDestino = estadoDestino
        self.elemento = elemento
