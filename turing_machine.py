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
        if block == "L":  # Mover a la izquierda
            self.head_position -= 1
            if self.head_position < 0:
                self.head_position = 0  # Asegurar que no salga por la izquierda
        elif block == "R":  # Mover a la derecha
            self.head_position += 1
            if self.head_position >= len(self.tape):
                self.tape.append("_")  # Añadir un espacio en blanco si se sale de los límites
        elif block.startswith("X"):  # Escritura dinámica
            self.tape[self.head_position] = block[1:]  # Escribir el símbolo en la posición actual
        elif block.startswith("L_"):  # Desplazar a la izquierda hasta encontrar X
            target = block[2:]  # Extrae el carácter objetivo 'x'
            while self.head_position > 0:
                self.head_position -= 1
                if self.tape[self.head_position] == target:
                    break
        elif block.startswith("R_"):  # Desplazar a la derecha hasta encontrar X
            target = block[2:]  # Extrae el carácter objetivo 'x'
            while self.head_position < len(self.tape) - 1:
                self.head_position += 1
                if self.tape[self.head_position] == target:
                    break
        elif block.startswith("S_l"):  # Desplazar una cadena hacia la izquierda
            blank_index = self.tape[self.head_position:].index("_")
            for i in range(blank_index, self.head_position, -1):
                self.tape[i] = self.tape[i - 1]
            self.tape[self.head_position] = "_"
        elif block.startswith("S_r"):  # Desplazar una cadena hacia la derecha
            blank_index = self.tape[:self.head_position].index("_")
            for i in range(blank_index, self.head_position):
                self.tape[i] = self.tape[i + 1]
            self.tape[self.head_position] = "_"
        else:
            raise ValueError(f"Bloque desconocido: {block}")

        # Notificar a la interfaz sobre la actualización de la cinta
        if self.tape_update_callback:
            self.tape_update_callback(self.tape, self.head_position)

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

    def step(self):
        if self.state == "halt":
            print("La máquina ha llegado al estado de parada y se detiene.")
            return False  # Detener ejecución si llega al estado 'halt'
        
        current_symbol = self.tape[self.head_position]
        print(f"Current State: {self.state}, Current Symbol: '{current_symbol}'")
        
        if (self.state, current_symbol) in self.transition_table:
            construction_block, next_state = self.transition_table[(self.state, current_symbol)]
            self.execute_block(construction_block)
            self.state = next_state
            self.display_tape()
            return True
        else:
            print(f"No hay transición definida para el estado '{self.state}' y símbolo '{current_symbol}'. La máquina se detiene.")
            return False
        
    def get_next_block(self):
        """Determina el siguiente bloque basado en el estado actual y el símbolo del cabezal."""
        current_symbol = self.tape[self.head_position]
        transition_key = (self.current_state, current_symbol)

        print(f"Evaluando transición: Estado actual = {self.current_state}, Símbolo actual = {current_symbol}")
        
        if transition_key in self.transitions:
            block, next_state = self.transitions[transition_key]
            print(f"Transición encontrada: Ejecutando bloque '{block}', Nuevo estado = {next_state}")
            self.current_state = next_state  # Actualiza el estado
            return block
        else:
            print("No se encontró transición. Máquina en estado halt.")
            self.current_state = "halt"  # Detener si no hay transición definida
            return None
        
    def set_initial_state(self, state):
        self.initial_state = state
        self.current_state = state  # El estado actual comienza igual que el inicial

    def set_tape(self, tape):
        self.tape = tape
        self.head_position = 0  # Reinicia la posición del cabezal

    def set_transitions(self, transitions):
        self.transitions = transitions

    def reset(self):
        self.current_state = self.initial_state
        self.head_position = 0
        self.halted = False

    def set_tape_update_callback(self, callback):
        self.tape_update_callback = callback

"
Bien ahora creo que funciona perfecto esos bloques. Por otro lado, recordando que la cinta es infinita, estaba pensando que si yo hacia "R__", es decir, hacer la instruccion R hasta encontrar un espacio vacio que es lo que estaria luego de todos los elementos de la cinta, deberia de ampliarse la cinta para que ahora el cabezal este fuera de la cinta. No se si me explico, por lo que te dare un ejemplo: si yo tengo la cinta "0011" y el bloque que se ejecuta es "R__" entonces el cabezal deberia estar en la quinta posicion, es decir:
0011_
        ^
Esto deberia funcionar tanto para "R_" como para "L_". Tambien ten encuenta que supongamos que si tuviera la lista "0011_1" y estoy en el primer 0, y hago "R__" deberia de llevarme al "_" que esta en la cinta, mientras que si vuelvo a ejecutar "R__" deberia de llevarme a la derecha del ultimo 1 de la cinta
"