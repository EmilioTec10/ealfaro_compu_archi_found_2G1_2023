import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QWidget, QComboBox, QTextEdit, QSpinBox, QMessageBox, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt
from multiciclo import MultiCycleCPU
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

        # ComboBox para seleccionar el tipo de procesador
        self.processor_combo = QComboBox(self)
        self.processor_combo.addItems(["Select Processor", "Multiciclo", "Uniciclo"])
        layout.addWidget(self.processor_combo)

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

        # Text area for messages
        self.messages_text = QTextEdit(self)
        self.messages_text.setReadOnly(True)
        layout.addWidget(self.messages_text)

        self.timer = QTimer()
        self.timer.timeout.connect(self.run_cycle)

        self.cpu = None

    def start_simulation(self):
        processor_type = self.processor_combo.currentText()
        cycle_time = self.delay_spinbox.value() / 1000.0  # Convert to seconds
        if processor_type == "Multiciclo":
            self.cpu = MultiCycleCPU(cycle_time)
        elif processor_type == "Uniciclo":
            self.cpu = UniCycleCPU(cycle_time)
        else:
            QMessageBox.warning(self, "Warning", "Please select a processor type.")
            return

        self.cpu.messageChanged.connect(self.update_messages)
        self.reset()
        self.timer.start(self.delay_spinbox.value())
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_simulation(self):
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def run_cycle(self):
        if not self.cpu.run_cycle():
            self.stop_simulation()
            return
        self.update_ui()

    def reset(self):
        if self.cpu:
            self.cpu.reset()
            self.update_ui()

    def update_ui(self):
        self.messages_text.append(f"PC: {self.cpu.PC}")

    def update_messages(self, message):
        self.messages_text.append(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CPUWindow()
    window.show()
    sys.exit(app.exec_())
