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
                self.transitions, self.tape, self.head_position = self.load_csv_as_dict(file_path)
                self.current_state = "start"  # Estado inicial predeterminado
                self.halted = False  # Reiniciar estado de detención

                # Sincronizar con la máquina de Turing
                self.turing_machine.set_initial_state(self.current_state)
                self.turing_machine.set_tape(self.tape)
                self.turing_machine.set_transitions(self.transitions)
                self.turing_machine.head_position = self.head_position

                # Actualizar la interfaz
                self.update_ui_after_load()

                # Habilitar todos los botones
                self.step_button.config(state="normal")
                self.auto_button.config(state="normal")
                self.fast_button.config(state="normal")

                self.state_label.config(text="Archivo cargado con éxito. ¡Listo para ejecutar!")
            except ValueError as e:
                self.state_label.config(text=f"Error al cargar archivo: {str(e)}")
            except Exception as e:
                self.state_label.config(text=f"Error inesperado: {str(e)}")

    def load_csv_as_dict(self, filepath):
        """Carga un archivo CSV como un diccionario y realiza validaciones."""
        transitions = {}
        tape = []  # Por defecto, cinta vacía
        initial_symbol = None  # Símbolo inicial basado en la primera transición desde 'start'
        has_start_state = False
        has_tape = False

        with open(filepath, mode="r", newline="") as file:
            reader = csv.reader(file)
            for row_index, row in enumerate(reader):
                # Validar la cinta inicial
                if row[0] == "tape":
                    has_tape = True
                    tape = list(row[1]) if len(row) > 1 and row[1].strip() else []
                    if not tape:
                        raise ValueError(f"La cinta inicial en la línea {row_index + 1} está vacía.")
                
                # Validar transiciones
                elif len(row) == 4:  # Debe tener exactamente 4 columnas
                    key = (row[0], row[1])
                    value = (row[2], row[3])
                    if not row[0].strip() or not row[1].strip():
                        raise ValueError(f"Estado o símbolo vacío en la línea {row_index + 1}.")
                    if row[0] == "start":
                        has_start_state = True
                        # Establecer el símbolo inicial si es la primera transición desde 'start'
                        if initial_symbol is None:
                            initial_symbol = row[1]
                    transitions[key] = value
                
                # Formato inválido
                else:
                    raise ValueError(f"Formato inválido en la línea {row_index + 1}: {row}")
        
        # Validar que haya al menos una línea de cinta
        if not has_tape:
            raise ValueError("No se encontró una línea de cinta ('tape') en el archivo CSV.")
        
        # Validar que haya al menos una transición desde el estado "start"
        if not has_start_state:
            raise ValueError("No hay transiciones definidas desde el estado inicial 'start'.")

        # Determinar la posición inicial del cabezal
        if initial_symbol not in tape:
            raise ValueError(f"El símbolo inicial '{initial_symbol}' definido en 'start' no se encuentra en la cinta.")
        head_position = tape.index(initial_symbol)

        return transitions, tape, head_position

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
            label = tk.Label(self.tape_frame, text=symbol, font=("Arial", 16), width=2, borderwidth=2, relief="solid")
            label.grid(row=0, column=i, padx=2, pady=10)  # Espaciado consistente
            self.tape_labels.append(label)

        # Eliminar cualquier configuración previa de expansión
        for i in range(len(self.tape)):
            self.tape_frame.grid_columnconfigure(i, weight=0)  # No permitir que las columnas se expandan

        # Centrar la cinta en la ventana
        self.root.grid_columnconfigure(0, weight=1)  # Centrar el frame principal
        self.root.grid_rowconfigure(0, weight=1)

        # Actualizar la posición inicial del cabezal
        self.update_head_position()

        # Actualizar o crear la etiqueta del estado
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
            self.state_label.config(text="No hay transición definida para el estado actual.")
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
            self.auto_speed = 1000  # Ajustar a velocidad estándar
        else:
            print("Iniciando avance automático estándar.")  # Depuración
            self.auto_stepping = True
            self.auto_speed = 1000  # Velocidad estándar
            self.perform_auto_step()

    def start_fast_step(self):
        """Inicia el avance automático con velocidad rápida."""
        if self.auto_stepping:
            print("La automatización ya está activa. Ajustando velocidad a rápida.")  # Depuración
            self.auto_speed = 200  # Ajustar a velocidad rápida
        else:
            print("Iniciando avance rápido.")  # Depuración
            self.auto_stepping = True
            self.auto_speed = 200  # Velocidad rápida
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
