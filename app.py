import csv
import tkinter as tk
from tkinter import filedialog as fd
from turing_machine import TuringMachine

class TuringMachineGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simulador de Máquina de Turing")

        # Crear una instancia de TuringMachine
        self.turing_machine = TuringMachine()

        # Configurar el comportamiento del grid para redimensionamiento
        self.root.grid_rowconfigure(0, weight=0)  # Fila de la cinta
        self.root.grid_rowconfigure(1, weight=0)  # Fila del estado
        self.root.grid_rowconfigure(2, weight=0)  # Fila del botón
        self.root.grid_columnconfigure(0, weight=1)  # Columna principal

        # Inicializar atributos
        self.tape = []
        self.head_position = 0
        self.current_state = None
        self.transitions = {}
        self.blocks = self.load_blocks("blocks.csv")
        self.halted = False
        self.auto_stepping = False  # Controla si el avance automático está activo
        self.auto_speed = 5000  # Intervalo en milisegundos para el avance automático

        self.tape_labels = []
        self.create_tape_display()

        # Botón para avanzar
        self.step_button = tk.Button(self.root, text="Siguiente Paso", command=self.execute_step)
        self.step_button.grid(row=2, column=0, sticky="ew", pady=10)  # Expandirse horizontalmente

        # Botón para avanzar automáticamente
        self.auto_button = tk.Button(self.root, text="Avanzar Automáticamente", command=self.start_auto_step)
        self.auto_button.grid(row=2, column=1, sticky="ew", pady=10)

        # Botón para avanzar rápidamente
        self.fast_button = tk.Button(self.root, text="Avanzar Rápido", command=self.start_fast_step)
        self.fast_button.grid(row=2, column=3, sticky="ew", pady=10)

        # Botón para cargar un archivo CSV
        self.load_csv_button = tk.Button(self.root, text="Cargar CSV de Transiciones", command=self.load_csv)
        self.load_csv_button.grid(row=1, column=1, pady=10, sticky="ew")

        self.turing_machine.set_tape_update_callback(self.update_tape_visual)

    def load_csv(self):
        """Permite al usuario cargar un nuevo archivo CSV de transiciones y cinta inicial."""
        file_path = fd.askopenfilename(
            title="Seleccionar archivo CSV de transiciones",
            filetypes=[("Archivos CSV", "*.csv")]
        )
        if file_path:
            try:
                # Cargar datos desde el archivo CSV con validaciones
                transitions, tape, initial_state, head_position = self.load_csv_as_dict(file_path)

                # Sincronizar con la máquina de Turing
                self.turing_machine.set_initial_state(initial_state)
                self.turing_machine.set_tape(tape)
                self.turing_machine.set_transitions(transitions)
                self.turing_machine.head_position = head_position

                # Actualizar el atributo local de la cinta
                self.tape = tape
                self.head_position = head_position
                self.current_state = initial_state

                # Actualizar la interfaz
                self.update_ui_after_load()

                # Habilitar los botones
                self.step_button.config(state="normal")
                self.auto_button.config(state="normal")
                self.fast_button.config(state="normal")
                self.state_label.config(text="Archivo cargado con éxito. ¡Listo para ejecutar!")

                self.turing_machine.error = False
                self.turing_machine.errorMensage = ""

            except ValueError as e:
                self.state_label.config(text=f"Error al cargar archivo: {str(e)}")
            except Exception as e:
                self.state_label.config(text=f"Error inesperado: {str(e)}")

    def load_csv_as_dict(self, filepath):
        """Carga un archivo CSV como un diccionario y realiza validaciones."""
        transitions = {}
        tape = []  # Por defecto, cinta vacía
        initial_state = None  # Estado inicial predeterminado
        head_position = None  # Posición inicial del cabezal

        with open(filepath, mode="r", newline="") as file:
            reader = csv.reader(file)
            for row_index, row in enumerate(reader):
                # Validar la cinta inicial
                if row[0] == "tape":
                    tape = list(row[1]) if len(row) > 1 and row[1].strip() else []
                    if not tape:
                        raise ValueError(f"La cinta inicial en la línea {row_index + 1} está vacía.")

                # Leer estado inicial
                elif row[0] == "initial_state":
                    if len(row) != 2 or not row[1].strip():
                        raise ValueError(f"El estado inicial está mal definido en la línea {row_index + 1}.")
                    initial_state = row[1].strip()

                elif row[0] == "head_position":
                    if len(row) != 2 or not row[1].isdigit():
                        raise ValueError(f"La posición inicial del cabezal está mal definida en la línea {row_index + 1}.")
                    head_position = int(row[1])
                    # Validar que la posición sea válida
                    if head_position < 0 or head_position >= len(tape):
                        raise ValueError(f"La posición inicial del cabezal '{head_position}' está fuera de los límites de la cinta.")
                    print("head_position: " + head_position.__str__())

                # Validar transiciones
                elif len(row) == 4:  # Debe tener exactamente 4 columnas
                    key = (row[0], row[1])
                    print("Key:" + key.__str__())
                    value = (row[2], row[3])
                    print("Value:" + value.__str__())
                    transitions[key] = value
                    if not row[0].strip() or not row[1].strip() or not row[2].strip() or not row[3].strip():
                        raise ValueError(f"Estado o símbolo vacío en la línea {row_index + 1}.")

                # Formato inválido
                else:
                    raise ValueError(f"Formato inválido en la línea {row_index + 1}: {row}")

        # Validaciones finales
        if not tape:
            raise ValueError("No se encontró una línea de cinta ('tape') en el archivo CSV.")
        if not initial_state:
            raise ValueError("No se encontró el estado inicial ('initial_state') en el archivo CSV.")
        if len(str(head_position)) == 0 or head_position == None:
            raise ValueError("No se encontró la posición inicial del cabezal ('head_position') en el archivo CSV.")
        if not transitions:
            raise ValueError("No se encontró transiciones en el archivo CSV.")

        return transitions, tape, initial_state, head_position

    def update_ui_after_load(self):
        """Actualiza la interfaz después de cargar un archivo CSV."""
        # Actualizar la representación de la cinta
        self.clear_tape_display()
        self.create_tape_display()

        # Configurar la posición inicial del cabezal
        self.update_tape_visual(self.tape, self.head_position)

        # Habilitar el botón de avance
        self.step_button.config(state="normal")

    def clear_tape_display(self):
        """Elimina la representación actual de la cinta y reorganiza el frame."""
        if hasattr(self, 'tape_frame'):
            for label in self.tape_labels:
                label.destroy()
            self.tape_labels = []
            self.tape_frame.destroy()

    def create_tape_display(self):
        """Crea o actualiza la representación visual de la cinta."""
        # Crear un nuevo frame para la cinta
        self.tape_frame = tk.Frame(self.root)
        self.tape_frame.grid(row=0, column=1, sticky="nsew")  # Asegurar que ocupe toda la celda del grid

        # Crear etiquetas para cada elemento de la cinta
        for i, symbol in enumerate(self.tape):
            bg_color = "yellow" if i == self.head_position else "white"
            label = tk.Label(self.tape_frame, text=symbol, font=("Arial", 16), width=2, borderwidth=2, relief="solid", bg=bg_color)
            label.grid(row=0, column=i, padx=2, pady=10)
            self.tape_labels.append(label)

        # Centrar la cinta en la ventana
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Actualizar el texto del estado inicial
        if not hasattr(self, 'state_label'):
            self.state_label = tk.Label(self.root, text=f"Estado: {self.current_state}", font=("Arial", 14), anchor="center")
            self.state_label.grid(row=3, column=1, sticky="ew", pady=10)
        else:
            self.state_label.config(text=f"Estado: {self.current_state}")

    def execute_step(self, stop_automation=True):
        """Ejecuta un paso de la máquina de Turing y detiene la automatización si se indica."""
        # Detener el avance automático si está activo
        if stop_automation and self.auto_stepping:
            print("Automatización detenida por el botón 'Siguiente Paso'.")  # Depuración
            self.auto_stepping = False

        if not self.turing_machine.transitions or not self.turing_machine.tape:
            self.state_label.config(text="Cargue un archivo CSV válido antes de continuar.")
            return

        block = self.turing_machine.get_next_block()
        if block:
            # Ejecutar el bloque
            self.turing_machine.execute_block(block)
            self.update_tape_visual(self.turing_machine.tape, self.turing_machine.head_position)

            # Verificar si la máquina llegó al estado de detención
            if self.turing_machine.error == True:
                self.state_label.config(
                    text=f"Estado: {self.turing_machine.current_state}, Bloque: {block}. {self.turing_machine.errorMensage}"
                )
                self.step_button.config(state="disabled")
                self.auto_button.config(state="disabled")
                self.fast_button.config(state="disabled")
                self.auto_stepping = False
            else:
                if self.turing_machine.current_state == "halt":
                    self.state_label.config(
                        text=f"Estado: {self.turing_machine.current_state}, Bloque: {block}. La máquina se ha detenido."
                    )
                    self.step_button.config(state="disabled")
                    self.auto_button.config(state="disabled")
                    self.fast_button.config(state="disabled")
                    self.auto_stepping = False
                else:
                    # Actualizar el texto del estado y bloque ejecutado
                    self.state_label.config(text=f"Estado: {self.turing_machine.current_state}, Bloque: {block}")
        else:
            self.state_label.config(text=f"Estado: {self.turing_machine.current_state}, Bloque: {block}. No hay transición definida para el estado actual.")
            self.step_button.config(state="disabled")
            self.auto_button.config(state="disabled")
            self.fast_button.config(state="disabled")
            self.auto_stepping = False

    def ensure_infinite_tape(self):
        """Asegura que la cinta sea infinita al expandir con espacios vacíos según sea necesario."""
        if self.head_position < 0:
            # Agregar un espacio vacío al inicio de la cinta
            self.tape.insert(0, "_")
            self.head_position = 0

            # Crear una nueva etiqueta para el espacio vacío
            label = tk.Label(self.tape_frame, text="_", font=("Arial", 16), width=2, borderwidth=2, relief="solid")
            self.tape_labels.insert(0, label)

            # Reubicar todas las etiquetas existentes
            for i, lbl in enumerate(self.tape_labels):
                lbl.grid(row=0, column=i, padx=2, pady=10)

        elif self.head_position >= len(self.tape):
            # Agregar un espacio vacío al final de la cinta
            self.tape.append("_")
            label = tk.Label(self.tape_frame, text="_", font=("Arial", 16), width=2, borderwidth=2, relief="solid")
            label.grid(row=0, column=len(self.tape_labels), padx=2, pady=10)
            self.tape_labels.append(label)

    def update_tape_visual(self, tape, head_position):
        """Actualiza la cinta visual en la interfaz."""
        # Limpiar etiquetas actuales
        for label in self.tape_labels:
            label.destroy()
        self.tape_labels = []

        # Crear etiquetas para la cinta actualizada
        for i, symbol in enumerate(tape):
            bg_color = "yellow" if i == head_position else "white"
            label = tk.Label(self.tape_frame, text=symbol, font=("Arial", 16), width=2, borderwidth=2, relief="solid", bg=bg_color)
            label.grid(row=0, column=i, padx=2, pady=2)
            self.tape_labels.append(label)

    def update_head_position(self):
        """Destaca la posición del cabezal en la cinta."""
        for i, label in enumerate(self.tape_labels):
            if i == self.head_position:
                label.config(bg="yellow")
            else:
                label.config(bg="white")

    def load_blocks(self, filepath):
        blocks = {}
        with open(filepath, mode="r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                blocks[row[0]] = row[1]
        return blocks
    
    def start_auto_step(self):
        """Inicia el avance automático con velocidad estándar."""
        if self.auto_stepping:
            print("La automatización ya está activa. Ajustando velocidad a estándar.")  # Depuración
            self.auto_speed = 300  # Ajustar a velocidad estándar
        else:
            print("Iniciando avance automático estándar.")  # Depuración
            self.auto_stepping = True
            self.auto_speed = 300  # Velocidad estándar
            self.perform_auto_step()

    def start_fast_step(self):
        """Inicia el avance automático con velocidad rápida."""
        if self.auto_stepping:
            print("La automatización ya está activa. Ajustando velocidad a rápida.")  # Depuración
            self.auto_speed = 50  # Ajustar a velocidad rápida
        else:
            print("Iniciando avance rápido.")  # Depuración
            self.auto_stepping = True
            self.auto_speed = 50  # Velocidad rápida
            self.perform_auto_step()

    def perform_auto_step(self):
        """Ejecuta pasos automáticamente mientras esté activo."""
        if self.auto_stepping:
            print("Ejecutando paso automático...")  # Depuración
            self.execute_step(stop_automation=False)  # No detener la automatización

            # Verifica si la máquina se detuvo
            if self.turing_machine.current_state == "halt":
                print("La máquina se ha detenido.")  # Depuración
                self.auto_stepping = False
                self.auto_button.config(state="disabled")
                self.fast_button.config(state="disabled")
            else:
                # Programa el siguiente paso si no está en halt
                self.root.after(self.auto_speed, self.perform_auto_step)

    def run(self):
        self.root.mainloop()

# Crear la GUI
gui = TuringMachineGUI()
gui.run()
