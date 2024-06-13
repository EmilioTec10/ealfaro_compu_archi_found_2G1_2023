import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QWidget, QComboBox, QTextEdit, QTableWidget, \
    QTableWidgetItem, QHBoxLayout, QSpinBox, QMessageBox, QGridLayout, QSizePolicy
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap
from multiciclo import MultiCycleCPU
from pipeline import PipelineCPU  # Asegúrate de que el nombre y la clase coincidan con tu implementación
import time

from uniciclo import UniCycleCPU

class CPUWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CPU Simulator")
        self.setFixedSize(600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        # Botón para seleccionar el tipo de interfaz
        self.interface_button = QPushButton("Interfaz de Uniciclo")
        self.interface_button.clicked.connect(self.show_cpu_simulation)
        layout.addWidget(self.interface_button)

        # Botón para cambiar a la interfaz de multiciclo
        self.multiciclo_button = QPushButton("Interfaz de Multiciclo")
        self.multiciclo_button.clicked.connect(self.show_multiciclo_interface)
        layout.addWidget(self.multiciclo_button)

        self.pipeline_button = QPushButton("Interfaz de Pipeline")  # Nuevo botón para el procesador segmentado
        self.pipeline_button.clicked.connect(self.show_pipeline_interface)
        layout.addWidget(self.pipeline_button)

        self.cpu_window = None
        self.multiciclo_window = None
        self.pipeline_window = None  # Variable para la nueva ventana del procesador segmentado


    def show_cpu_simulation(self):
        if self.cpu_window is None:
            self.cpu_window = CPUSimulationWindow()
        self.cpu_window.show()

    def show_multiciclo_interface(self):
        if self.multiciclo_window is None:
            self.multiciclo_window = MulticicloWindow()
        self.multiciclo_window.show()

    def show_pipeline_interface(self):  # Método para mostrar la interfaz del procesador segmentado
        if self.pipeline_window is None:
            self.pipeline_window = PipelineCPUWindow()
        self.pipeline_window.show()

class CPUSimulationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UniCycle CPU Simulator")
        self.setFixedSize(800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        # SpinBox para seleccionar el delay en milisegundos
        delay_layout = QHBoxLayout()
        self.delay_label = QLabel("Delay (ms):")
        delay_layout.addWidget(self.delay_label)
        self.delay_spinbox = QSpinBox(self)
        self.delay_spinbox.setRange(0, 1000)  # Rango de 0 a 1 segundo
        self.delay_spinbox.setValue(100)  # Valor por defecto: 100 ms
        delay_layout.addWidget(self.delay_spinbox)
        layout.addLayout(delay_layout)

        # Botones para controlar la ejecución
        self.start_button = QPushButton("Start Simulation")
        self.start_button.clicked.connect(self.start_simulation)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Simulation")
        self.stop_button.clicked.connect(self.stop_simulation)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

        # Botón para Step-by-Step Execution
        self.step_button = QPushButton("Step-by-Step Execution")
        self.step_button.clicked.connect(self.run_step)
        layout.addWidget(self.step_button)

        # Botón para regresar
        self.return_button = QPushButton("Return")
        self.return_button.clicked.connect(self.return_to_main)
        layout.addWidget(self.return_button)

        # Crear y agregar etiquetas para cada área de texto
        self.label_fetched = QLabel("Fetched", self)
        layout.addWidget(self.label_fetched)
        self.fetched_text = QTextEdit(self)
        self.fetched_text.setReadOnly(True)
        layout.addWidget(self.fetched_text)

        self.label_decoded = QLabel("Decoded", self)
        layout.addWidget(self.label_decoded)
        self.decoded_text = QTextEdit(self)
        self.decoded_text.setReadOnly(True)
        layout.addWidget(self.decoded_text)

        self.label_executed = QLabel("Executed", self)
        layout.addWidget(self.label_executed)
        self.executed_text = QTextEdit(self)
        self.executed_text.setReadOnly(True)
        layout.addWidget(self.executed_text)

        self.label_memory_access = QLabel("Memory Access", self)
        layout.addWidget(self.label_memory_access)
        self.memory_access_text = QTextEdit(self)
        self.memory_access_text.setReadOnly(True)
        layout.addWidget(self.memory_access_text)

        self.label_write_back = QLabel("Write Back", self)
        layout.addWidget(self.label_write_back)
        self.write_back_text = QTextEdit(self)
        self.write_back_text.setReadOnly(True)
        layout.addWidget(self.write_back_text)

        # Text area for messages
        self.messages_text = QTextEdit(self)
        self.messages_text.setReadOnly(True)
        layout.addWidget(self.messages_text)

        # Text area for execution time
        self.execution_time_label = QLabel("Execution Time (s):", self)
        layout.addWidget(self.execution_time_label)
        self.execution_time_text = QTextEdit(self)
        self.execution_time_text.setReadOnly(True)
        layout.addWidget(self.execution_time_text)

        self.timer = QTimer()
        self.timer.timeout.connect(self.run_cycle)
        self.cpu = None
        self.start_time = None

    def start_simulation(self):
        processor_type = "Uniciclo"
        cycle_time = self.delay_spinbox.value() / 1000.0  # Convert to seconds
        self.cpu = UniCycleCPU(cycle_time)

        self.cpu.messageChanged.connect(self.update_messages)
        self.reset()
        self.timer.start(self.delay_spinbox.value())
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.start_time = time.time()

    def stop_simulation(self):
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.update_execution_time()

    def run_cycle(self):
        if not self.cpu.run_cycle():
            self.stop_simulation()
            return
        self.update_ui()

    def run_step(self):
        if not self.cpu.run_cycle():
            self.step_button.setEnabled(False)
        self.update_ui()

    def reset(self):
        if self.cpu:
            self.cpu.reset()
            self.update_ui()

    def update_ui(self):
        self.messages_text.append(f"PC: {self.cpu.PC}")
        self.update_execution_time()

    def update_messages(self, message):
        # Dividir el mensaje en partes
        parts = message.split(': ')

        if len(parts) == 2:
            category, content = parts[0], parts[1]

            # Limpiar la caja de texto correspondiente
            if category == 'Fetched':
                self.fetched_text.clear()
            elif category == 'Decoded':
                self.decoded_text.clear()
            elif category == 'Executed':
                self.executed_text.clear()
            elif category == 'Memory Access':
                self.memory_access_text.clear()
            elif category == 'Write Back':
                self.write_back_text.clear()

            # Actualizar la caja de texto correspondiente
            if category == 'Fetched':
                self.fetched_text.append(content)
            elif category == 'Decoded':
                self.decoded_text.append(content)
            elif category == 'Executed':
                self.executed_text.append(content)
            elif category == 'Memory Access':
                self.memory_access_text.append(content)
            elif category == 'Write Back':
                self.write_back_text.append(content)

    def update_execution_time(self):
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            self.execution_time_text.setPlainText(f"{elapsed_time:.2f}")

    def return_to_main(self):
        # Cerrar la ventana actual y mostrar la ventana principal
        self.close()

class MulticicloWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MultiCycle CPU Simulator")
        self.setFixedSize(780, 715)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        self.return_button = QPushButton("Regresar")
        self.return_button.clicked.connect(self.close_and_return)
        layout.addWidget(self.return_button)

        # SpinBox para seleccionar el delay en centisegundos
        delay_layout = QHBoxLayout()
        self.delay_label = QLabel("Delay (ms):")
        delay_layout.addWidget(self.delay_label)
        self.delay_spinbox = QSpinBox(self)
        self.delay_spinbox.setRange(0, 100)  # Rango de 0 a 1 segundo en centisegundos
        self.delay_spinbox.setValue(30)  # Valor por defecto: 0.1 segundo (10 centisegundos)
        delay_layout.addWidget(self.delay_spinbox)
        layout.addLayout(delay_layout)

        # SpinBox para seleccionar la cantidad de datos a mostrar de self.cpu.data_memory
        data_layout = QHBoxLayout()
        self.data_label = QLabel("Data Memory Size:")
        data_layout.addWidget(self.data_label)
        self.data_spinbox = QSpinBox(self)
        self.data_spinbox.setRange(0, 1024)  # Rango de 0 a 1024 (tamaño máximo de la memoria de datos)
        self.data_spinbox.setValue(27)  # Valor por defecto: 10 datos
        data_layout.addWidget(self.data_spinbox)
        layout.addLayout(data_layout)

        # Botones para controlar la ejecución
        self.start_button = QPushButton("Start Simulation")
        self.start_button.clicked.connect(self.start_simulation)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Simulation")
        self.stop_button.clicked.connect(self.stop_simulation)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

        self.step_button = QPushButton("Step-by-Step Execution")
        self.step_button.clicked.connect(self.run_step)
        layout.addWidget(self.step_button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset)
        layout.addWidget(self.reset_button)

        # Layout for text areas
        text_area_layout = QGridLayout()
        layout.addLayout(text_area_layout)

        # Program Counter
        self.pc_label = QLabel("Program Counter:")
        text_area_layout.addWidget(self.pc_label, 0, 0)
        self.pc_text = QTextEdit(self)
        self.pc_text.setReadOnly(True)
        self.pc_text.setFixedWidth(240)
        self.pc_text.setFixedHeight(50)  # Adjust the height as needed
        text_area_layout.addWidget(self.pc_text, 1, 0)

        # FSM State
        self.fsm_label = QLabel("FSM State:")
        text_area_layout.addWidget(self.fsm_label, 0, 1)
        self.fsm_text = QTextEdit(self)
        self.fsm_text.setReadOnly(True)
        self.fsm_text.setFixedWidth(240)
        self.fsm_text.setFixedHeight(50)  # Adjust the height as needed
        text_area_layout.addWidget(self.fsm_text, 1, 1)

        # Memory and Registers
        self.memory_label = QLabel("Memory:")
        text_area_layout.addWidget(self.memory_label, 2, 0)
        self.memory_text = QTextEdit(self)
        self.memory_text.setReadOnly(True)
        self.memory_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        text_area_layout.addWidget(self.memory_text, 3, 0)
        self.memory_text.setFixedWidth(240)  # Adjust the height as needed

        self.registers_label = QLabel("Registers:")
        text_area_layout.addWidget(self.registers_label, 2, 1)
        self.registers_text = QTextEdit(self)
        self.registers_text.setReadOnly(True)
        self.registers_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        text_area_layout.addWidget(self.registers_text, 3, 1)
        self.registers_text.setFixedWidth(240)

        # Image
        self.image_label = QLabel(self)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        text_area_layout.addWidget(self.image_label, 0, 2, 0, 3)

        # Add image next to FSM state box
        image_path = "FSM_STATES/MAQUINA.png"  # Replace with your image path

        if os.path.exists(image_path):
            self.image_label.setPixmap(QPixmap(image_path))
        else:
            QMessageBox.critical(self, "Error", f"Image file not found: {image_path}")
            # Optionally, set a default image or handle the missing file case
            self.image_label.setText("Image not found")

        # Tabla para mostrar el historial de ejecuciones
        self.history_table = QTableWidget(0, 3)
        self.history_table.setHorizontalHeaderLabels(["Processor", "Cycles", "Execution Time"])
        text_area_layout.addWidget(self.history_table, 4, 0, 1, 0)
        self.history_table.setFixedWidth(486)
        self.history_table.setFixedHeight(175)

        self.cpu = MultiCycleCPU()
        self.cpu.messageChanged.connect(self.update_output)
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_cycle)

        self.execution_history = []  # Historial de ejecuciones

    def start_simulation(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.step_button.setEnabled(False)
        self.cpu.reset()
        delay = self.delay_spinbox.value()
        self.timer.start(delay * 10)  # centisegundos

    def stop_simulation(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.step_button.setEnabled(True)
        self.timer.stop()

    def close_and_return(self):
        self.close()

    def run_cycle(self):
        if not self.cpu.run_cycle():
            self.stop_simulation()
        self.update_status()

    def run_step(self):
        if not self.cpu.run_cycle():
            self.step_button.setEnabled(False)
        self.update_status()

    def reset(self):
        if self.start_button.isEnabled():
            self.step_button.setEnabled(True)
        self.cpu.reset()
        self.update_status()

    def update_output(self, message):
        self.pc_text.append(message)
        self.registers_text.append(message)
        self.memory_text.append(message)
        self.fsm_text.append(message)

        # Prevent auto-scroll up
        self.prevent_auto_scroll(self.pc_text)
        self.prevent_auto_scroll(self.registers_text)
        self.prevent_auto_scroll(self.memory_text)
        self.prevent_auto_scroll(self.fsm_text)

    def update_status(self):
        elapsed_time = time.time() - self.cpu.start_time if self.cpu.start_time else 0
        self.pc_text.setPlainText(f"PC: {self.cpu.PC}")
        self.registers_text.setPlainText(f"Registers: {self.cpu.registers}")
        data_memory_size = self.data_spinbox.value()
        self.memory_text.setPlainText(f"Memory: {self.cpu.data_memory[:data_memory_size]}")
        self.fsm_text.setPlainText(f"FSM State: {self.cpu.state}")
        self.image_label.setPixmap(QPixmap(f"FSM_STATES\\{self.cpu.state}.png"))

        # Prevent auto-scroll up
        self.prevent_auto_scroll(self.pc_text)
        self.prevent_auto_scroll(self.registers_text)
        self.prevent_auto_scroll(self.memory_text)
        self.prevent_auto_scroll(self.fsm_text)

        self.log_execution("Multiciclo")

    def prevent_auto_scroll(self, text_edit):
        cursor = text_edit.textCursor()
        cursor.movePosition(cursor.End)
        text_edit.setTextCursor(cursor)
        text_edit.ensureCursorVisible()

    def log_execution(self, processor_type):
        row_count = self.history_table.rowCount()
        self.history_table.insertRow(row_count)
        self.history_table.setItem(row_count, 0, QTableWidgetItem(processor_type))
        self.history_table.setItem(row_count, 1, QTableWidgetItem(str(self.cpu.PC)))
        self.history_table.setItem(row_count, 2, QTableWidgetItem(f"{time.time() - self.cpu.start_time:.2f}s"))

        self.execution_history.append(
            (processor_type, self.cpu.PC, time.time() - self.cpu.start_time))
        if len(self.execution_history) > 5:
            self.execution_history.pop(0)
            self.history_table.removeRow(0)

class PipelineCPUWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pipeline CPU Simulator")
        self.setFixedSize(800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        delay_layout = QHBoxLayout()
        self.delay_label = QLabel("Delay (ms):")
        delay_layout.addWidget(self.delay_label)
        self.delay_spinbox = QSpinBox(self)
        self.delay_spinbox.setRange(0, 1000)  # Rango de 0 a 1 segundo
        self.delay_spinbox.setValue(100)  # Valor por defecto: 100 ms
        delay_layout.addWidget(self.delay_spinbox)
        layout.addLayout(delay_layout)

        self.start_button = QPushButton("Start Simulation")
        self.start_button.clicked.connect(self.start_simulation)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Simulation")
        self.stop_button.clicked.connect(self.stop_simulation)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

        self.step_button = QPushButton("Step-by-Step Execution")
        self.step_button.clicked.connect(self.run_step)
        layout.addWidget(self.step_button)

        self.return_button = QPushButton("Return")
        self.return_button.clicked.connect(self.return_to_main)
        layout.addWidget(self.return_button)

        self.label_fetched = QLabel("Fetched", self)
        layout.addWidget(self.label_fetched)
        self.fetched_text = QTextEdit(self)
        self.fetched_text.setReadOnly(True)
        layout.addWidget(self.fetched_text)

        self.label_decoded = QLabel("Decoded", self)
        layout.addWidget(self.label_decoded)
        self.decoded_text = QTextEdit(self)
        self.decoded_text.setReadOnly(True)
        layout.addWidget(self.decoded_text)

        self.label_executed = QLabel("Executed", self)
        layout.addWidget(self.label_executed)
        self.executed_text = QTextEdit(self)
        self.executed_text.setReadOnly(True)
        layout.addWidget(self.executed_text)

        self.label_memory_access = QLabel("Memory Access", self)
        layout.addWidget(self.label_memory_access)
        self.memory_access_text = QTextEdit(self)
        self.memory_access_text.setReadOnly(True)
        layout.addWidget(self.memory_access_text)

        self.label_write_back = QLabel("Write Back", self)
        layout.addWidget(self.label_write_back)
        self.write_back_text = QTextEdit(self)
        self.write_back_text.setReadOnly(True)
        layout.addWidget(self.write_back_text)

        self.messages_text = QTextEdit(self)
        self.messages_text.setReadOnly(True)
        layout.addWidget(self.messages_text)

        self.execution_time_label = QLabel("Execution Time (s):", self)
        layout.addWidget(self.execution_time_label)
        self.execution_time_text = QTextEdit(self)
        self.execution_time_text.setReadOnly(True)
        layout.addWidget(self.execution_time_text)

        self.timer = QTimer()
        self.timer.timeout.connect(self.run_cycle)
        self.cpu = None
        self.start_time = None

    def start_simulation(self):
        cycle_time = self.delay_spinbox.value() / 1000.0  # Convert to seconds
        self.cpu = PipelineCPU(cycle_time)

        self.cpu.messageChanged.connect(self.update_messages)
        self.reset()
        self.timer.start(self.delay_spinbox.value())
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.start_time = time.time()

    def stop_simulation(self):
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.update_execution_time()

    def run_cycle(self):
        if not self.cpu.run_cycle():
            self.stop_simulation()
            return
        self.update_ui()

    def run_step(self):
        if not self.cpu.run_cycle():
            self.step_button.setEnabled(False)
        self.update_ui()

    def reset(self):
        if self.cpu:
            self.cpu.reset()
            self.update_ui()

    def update_ui(self):
        self.messages_text.append(f"PC: {self.cpu.PC}")
        self.update_execution_time()

    def update_messages(self, message):
        parts = message.split(': ')

        if len(parts) == 2:
            category, content = parts[0], parts[1]

            if category == 'Fetched':
                self.fetched_text.clear()
            elif category == 'Decoded':
                self.decoded_text.clear()
            elif category == 'Executed':
                self.executed_text.clear()
            elif category == 'Memory Access':
                self.memory_access_text.clear()
            elif category == 'Write Back':
                self.write_back_text.clear()

            if category == 'Fetched':
                self.fetched_text.append(content)
            elif category == 'Decoded':
                self.decoded_text.append(content)
            elif category == 'Executed':
                self.executed_text.append(content)
            elif category == 'Memory Access':
                self.memory_access_text.append(content)
            elif category == 'Write Back':
                self.write_back_text.append(content)

    def update_execution_time(self):
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            self.execution_time_text.setPlainText(f"{elapsed_time:.2f}")

    def return_to_main(self):
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CPUWindow()
    window.show()
    sys.exit(app.exec_())
