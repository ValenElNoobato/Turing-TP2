import csv

class TuringMachine:
    def __init__(self):
        self.initial_state = None  # Estado inicial
        self.current_state = None  # Estado actual
        self.tape = []  # La cinta de la máquina
        self.head_position = 0  # Posición inicial del cabezal
        self.transitions = {}  # Transiciones
        self.blocks = {}  # Bloques de construcción
        self.tape_update_callback = None  # Callback para actualizar la cinta
        self.error = False
        self.errorMensage = ""

    def load_transition_table(self, filename):
        transition_table = {}
        with open(filename, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                current_state, read_symbol, construction_block, next_state = row
                transition_table[(current_state, read_symbol)] = (construction_block, next_state)
        return transition_table

    def load_blocks_table(self, filename):
        blocks_table = {}
        with open(filename, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                block, action = row
                blocks_table[block] = action
        return blocks_table
    
    def display_tape(self):
        tape_str = ''.join(self.tape)
        head_str = ' ' * self.head_position + '^'
        print("Tape:", tape_str)
        print("Head:", head_str)
    
    def ensure_infinite_tape(self):
        # Expande la cinta hacia la izquierda si el cabezal está más allá del inicio
        if self.head_position < 0:
            self.tape.insert(0, self.blank_symbol)
            self.head_position = 0
        # Expande la cinta hacia la derecha si el cabezal está más allá del final
        elif self.head_position >= len(self.tape):
            self.tape.append(self.blank_symbol)
    
    def execute_block(self, block):
        """Ejecuta un bloque de construcción."""
        
        # Validar si el bloque existe en la tabla de bloques
        if block not in self.blocks and not block.startswith(("L", "R", "X", "R_", "L_", "S_l", "S_r")):
            self.errorMensage = f"Error: El bloque '{block}' no está definido en la tabla de bloques."
            self.current_state = "halt"
            return
        
        if block == "L":  # Mover a la izquierda
            self.head_position -= 1
            if self.head_position < 0:
                self.head_position = 0
        elif block == "R":  # Mover a la derecha
            self.head_position += 1
            if self.head_position >= len(self.tape):
                self.tape.append("_")
        elif block.startswith("X"):  # Escritura dinámica
            # Validar que tenga exactamente un carácter adicional
            if len(block[1:]) != 1:
                self.errorMensage = f"Error: El bloque '{block}' debe contener exactamente un carácter adicional."
                self.current_state = "halt"
                self.error = True
                return
            self.tape[self.head_position] = block[1:]
        elif block.startswith("R_"):  # Desplazar a la derecha hasta encontrar X
            target = block[2:]
            if len(target) != 1:
                self.errorMensage = f"Error: El bloque '{block}' debe contener exactamente un carácter como símbolo objetivo."
                self.current_state = "halt"
                self.error = True
                return
            found = False  # Bandera para verificar si el símbolo fue encontrado
            while not found:
                # Validar si el símbolo objetivo está presente desde la posición actual
                if target != "_" and target not in self.tape[self.head_position:]:
                    self.errorMensage = f"Error: El símbolo '{target}' no se encontró en la cinta hacia la derecha."
                    self.current_state = "halt"
                    self.error = True
                    return
                self.head_position += 1
                # Expandir la cinta si el cabezal está fuera de los límites
                if self.head_position >= len(self.tape):
                    if target == "_":  # Caso especial: buscar un espacio vacío
                        self.tape.append("_")
                        found = True
                    else:
                        self.tape.append("_")
                # Detenerse si encuentra el símbolo objetivo
                if self.tape[self.head_position] == target:
                    found = True
        elif block.startswith("L_"):  # Desplazar a la izquierda hasta encontrar X
            target = block[2:]
            if len(target) != 1:
                self.errorMensage = f"Error: El bloque '{block}' debe contener exactamente un carácter como símbolo objetivo."
                self.current_state = "halt"
                self.error = True
                return
            found = False  # Bandera para verificar si el símbolo fue encontrado
            while not found:
                # Validar si el símbolo objetivo está presente desde la posición actual
                if target != "_" and target not in self.tape[:self.head_position + 1]:
                    self.errorMensage = f"Error: El símbolo '{target}' no se encontró en la cinta hacia la izquierda."
                    self.current_state = "halt"
                    self.error = True
                    return
                self.head_position -= 1
                # Expandir la cinta si el cabezal está fuera de los límites
                if self.head_position < 0:
                    if target == "_":  # Caso especial: buscar un espacio vacío
                        self.tape.insert(0, "_")
                        self.head_position = 0
                        found = True
                    else:
                        self.tape.insert(0, "_")
                        self.head_position = 0
                # Detenerse si encuentra el símbolo objetivo
                if self.tape[self.head_position] == target:
                    found = True
            if not found:
                self.errorMensage = f"Error: El símbolo '{target}' no se encontró en la cinta hacia la izquierda."
                self.error = True
                self.current_state = "halt"

        elif block == "S_l":  # Desplazar a la izquierda los elementos a la derecha del puntero
            for i in range(self.head_position, len(self.tape) - 1):
                self.tape[i] = self.tape[i + 1]
            self.tape.pop()  # Eliminar el último elemento

            # Si el cabezal está fuera de los límites, agregar un espacio vacío
            if self.head_position >= len(self.tape):
                self.tape.append("_")
        elif block == "S_r":  # Desplazar a la derecha los elementos a la izquierda del puntero
            for i in range(self.head_position, 0, -1):
                self.tape[i] = self.tape[i - 1]
            self.tape.pop(0)  # Eliminar el primer elemento
            self.head_position -= 1  # Ajustar el puntero

            # Si el cabezal está fuera de los límites, agregar un espacio vacío
            if self.head_position < 0:
                self.tape.insert(0, "_")
                self.head_position = 0

    def shift_left(self):
        """Desplaza a la izquierda la cadena desde la posición actual hasta el primer espacio."""
        start = self.head_position
        end = start
        while end < len(self.tape) and self.tape[end] != "_":
            end += 1
        if end > start:
            for i in range(start, end - 1):
                self.tape[i] = self.tape[i + 1]
            self.tape[end - 1] = "_"

    def shift_right(self):
        """Desplaza a la derecha la cadena desde la posición actual hasta el primer espacio."""
        start = self.head_position
        end = start
        while start >= 0 and self.tape[start] != "_":
            start -= 1
        if start < end - 1:
            for i in range(end - 1, start, -1):
                self.tape[i] = self.tape[i - 1]
            self.tape[start + 1] = "_"
        
    def get_next_block(self):
        """Determina el siguiente bloque basado en el estado actual y el símbolo del cabezal."""
        current_symbol = self.tape[self.head_position]
        print(f"Evaluando transición: Estado actual = {self.current_state}, Símbolo actual = {current_symbol}")

        transition_key = (self.current_state, current_symbol)
        if transition_key in self.transitions:
            block, next_state = self.transitions[transition_key]
            print("next_state: " + next_state)
            if next_state.startswith("pause"):
                print(f"Estado especial detectado: {next_state}. Deteniendo la automatización.")
                self.errorMensage = "La automatización se pausó por un estado nombrado 'pause'."
            else:
                self.errorMensage = ""  # Limpiar mensaje de error si no es un estado "pause"
            self.current_state = next_state  # Actualiza el estado
            return block
        else:
            return None  # No hay transición definida
        
    def set_initial_state(self, state):
        self.initial_state = state
        self.current_state = state 

    def set_tape(self, tape):
        self.tape = tape

    def set_transitions(self, transitions):
        self.transitions = transitions

    def reset(self):
        self.current_state = self.initial_state
        self.head_position = 0
        self.halted = False

    def set_tape_update_callback(self, callback):
        self.tape_update_callback = callback

