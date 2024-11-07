cinta = []
posicion = cinta.count()

class Estado():
    def __init__(self, nombre: str):
        self.nombre = nombre

    def __str__(self):
        return self.nombre

    def __eq__(self, other):
        if not isinstance(other, Estado):
            return NotImplemented
        return self.nombre == other.nombre

class Transicion():
    def __init__(self, estadoInicial: Estado, estadoDestino: Estado, elemento: str, desplazamiento: any):        
        self.estadoInicial = estadoInicial
        self.estadoDestino = estadoDestino
        self.elemento = elemento
        self.desplazamiento = desplazamiento

def right():
    if (cinta):
        posicion += 1

def left():
    if (cinta):
        posicion -= 1
        