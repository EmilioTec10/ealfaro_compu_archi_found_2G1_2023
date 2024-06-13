import time
from PyQt5.QtCore import QThread, pyqtSignal

class PipelineCPU(QThread):
    messageChanged = pyqtSignal(str)

    def __init__(self, cycleTime=1):
        super().__init__()
        self.cycleTime = cycleTime  # Tiempo de ciclo en segundos
        self.reset()

    def reset(self):
        self.start_time = time.time()
        self.registers = [0] * 32  # Registros de propósito general
        self.memory = [0] * 1024  # Memoria unificada para instrucciones y datos
        self.instruction_memory = [None] * 256  # Memoria de instrucciones
        combined_memory = Memory().combined_memory
        self.memory[:len(combined_memory)] = combined_memory  # Cargar memoria combinada en la memoria de la CPU
        self.data_memory = [0] * 1024  # Memoria de datos
        self.PC = 0  # Contador de programa
        self.pipeline = {'IF': None, 'ID': None, 'EX': None, 'MEM': None, 'WB': None}  # Etapas del pipeline
        self.instruction_count = self.separate_memory()  # Separar memoria y obtener el conteo de instrucciones
        self.stalls = 0

    def fetch(self):
        if self.PC < self.instruction_count:
            self.pipeline['IF'] = self.instruction_memory[self.PC]
            self.PC += 1
            self.messageChanged.emit(f"Fetched: {self.pipeline['IF']}")
            print(f"Fetched: {self.pipeline['IF']}")

    def decode(self):
        if self.pipeline['IF']:
            self.pipeline['ID'] = self.pipeline['IF']
            self.pipeline['ID'].A = self.registers[self.pipeline['ID'].rs]
            self.pipeline['ID'].B = self.registers[self.pipeline['ID'].rt]
            self.messageChanged.emit(f"Decoded: A = {self.pipeline['ID'].A}, B = {self.pipeline['ID'].B}")
            print(f"Decoded: A = {self.pipeline['ID'].A}, B = {self.pipeline['ID'].B}")

    def execute(self):
        if self.pipeline['ID']:
            self.pipeline['EX'] = self.pipeline['ID']
            if self.pipeline['EX'].opcode == 'ADD':
                self.pipeline['EX'].ALUOut = self.pipeline['EX'].A + self.pipeline['EX'].B
            elif self.pipeline['EX'].opcode == 'SUB':
                self.pipeline['EX'].ALUOut = self.pipeline['EX'].A - self.pipeline['EX'].B
            elif self.pipeline['EX'].opcode == 'MUL':
                self.pipeline['EX'].ALUOut = self.pipeline['EX'].A * self.pipeline['EX'].B
            elif self.pipeline['EX'].opcode == 'LOAD':
                self.pipeline['EX'].ALUOut = self.pipeline['EX'].A + self.pipeline['EX'].imm
            elif self.pipeline['EX'].opcode == 'STORE':
                self.pipeline['EX'].ALUOut = self.pipeline['EX'].A + self.pipeline['EX'].imm
            elif self.pipeline['EX'].opcode == 'JUMP':
                self.pipeline['EX'].ALUOut = self.PC + self.pipeline['EX'].imm
            elif self.pipeline['EX'].opcode == 'BEQ':
                self.pipeline['EX'].ALUOut = self.PC + self.pipeline['EX'].imm if self.pipeline['EX'].A == self.pipeline['EX'].B else self.PC
            elif self.pipeline['EX'].opcode == 'AND':
                self.pipeline['EX'].ALUOut = self.pipeline['EX'].A & self.pipeline['EX'].B
            elif self.pipeline['EX'].opcode == 'OR':
                self.pipeline['EX'].ALUOut = self.pipeline['EX'].A | self.pipeline['EX'].B
            elif self.pipeline['EX'].opcode == 'XOR':
                self.pipeline['EX'].ALUOut = self.pipeline['EX'].A ^ self.pipeline['EX'].B
            elif self.pipeline['EX'].opcode == 'SLT':
                self.pipeline['EX'].ALUOut = 1 if self.pipeline['EX'].A < self.pipeline['EX'].B else 0
            elif self.pipeline['EX'].opcode == 'ADDI':
                self.pipeline['EX'].ALUOut = self.pipeline['EX'].A + self.pipeline['EX'].imm
            elif self.pipeline['EX'].opcode == 'SUBI':
                self.pipeline['EX'].ALUOut = self.pipeline['EX'].A - self.pipeline['EX'].imm
            elif self.pipeline['EX'].opcode == 'BNE':
                self.pipeline['EX'].ALUOut = self.PC + self.pipeline['EX'].imm if self.pipeline['EX'].A != self.pipeline['EX'].B else self.PC
            self.messageChanged.emit(f"Executed: ALUOut = {self.pipeline['EX'].ALUOut}")
            print(f"Executed: ALUOut = {self.pipeline['EX'].ALUOut}")

    def memory_access(self):
        if self.pipeline['EX']:
            self.pipeline['MEM'] = self.pipeline['EX']
            if self.pipeline['MEM'].opcode == 'LOAD':
                self.pipeline['MEM'].MDR = self.data_memory[self.pipeline['MEM'].ALUOut]
            elif self.pipeline['MEM'].opcode == 'STORE':
                self.data_memory[self.pipeline['MEM'].ALUOut] = self.pipeline['MEM'].B
            self.messageChanged.emit(f"Memory Access: MDR = {self.pipeline['MEM'].MDR}")
            print(f"Memory Access: MDR = {self.pipeline['MEM'].MDR}")

    def write_back(self):
        if self.pipeline['MEM']:
            self.pipeline['WB'] = self.pipeline['MEM']
            if self.pipeline['WB'].opcode in ['ADD', 'SUB', 'AND', 'OR', 'XOR', 'SLT', 'MUL']:
                self.registers[self.pipeline['WB'].rd] = self.pipeline['WB'].ALUOut
            elif self.pipeline['WB'].opcode == 'LOAD':
                self.registers[self.pipeline['WB'].rt] = self.pipeline['WB'].MDR
            elif self.pipeline['WB'].opcode in ['JUMP', 'BEQ', 'BNE']:
                self.PC = self.pipeline['WB'].ALUOut
            elif self.pipeline['WB'].opcode in ['ADDI', 'SUBI']:
                self.registers[self.pipeline['WB'].rt] = self.pipeline['WB'].ALUOut
            self.messageChanged.emit(f"Write Back: Registers = {self.registers}")
            print(f"Write Back: Registers = {self.registers}")

    def run_cycle(self):
        if self.PC >= self.instruction_count and all(stage is None for stage in self.pipeline.values()):
            return False

        self.write_back()
        self.memory_access()
        self.execute()
        self.decode()
        self.fetch()

        # Gestionar riesgos de datos con stalls
        if self.detect_data_hazard():
            self.stall_pipeline()
            self.messageChanged.emit(f"Stalled due to data hazard")
            print(f"Stalled due to data hazard")

        return True

    def detect_data_hazard(self):
        # Detectar riesgos de datos entre etapas ID y EX
        if self.pipeline['ID'] and self.pipeline['EX']:
            if self.pipeline['ID'].rs == self.pipeline['EX'].rd or self.pipeline['ID'].rt == self.pipeline['EX'].rd:
                return True
        return False

    def stall_pipeline(self):
        self.stalls += 1
        # Introducir un ciclo de stall moviendo las etapas hacia abajo y repitiendo la etapa ID
        self.pipeline['WB'] = self.pipeline['MEM']
        self.pipeline['MEM'] = self.pipeline['EX']
        self.pipeline['EX'] = None  # Introducir stall en la etapa EX
        # La etapa ID y IF permanecen sin cambios para repetir la instrucción en ID

    def separate_memory(self):
        instruction_count = 0
        for i, entry in enumerate(self.memory):
            if isinstance(entry, Instruction):
                self.instruction_memory[instruction_count] = entry
                instruction_count += 1
            else:
                break
        for j in range(instruction_count, len(self.memory)):
            self.data_memory[j - instruction_count] = self.memory[j]
        return instruction_count

class Instruction:
    def __init__(self, opcode, rs=0, rt=0, rd=0, imm=0):
        self.opcode = opcode
        self.rs = rs
        self.rt = rt
        self.rd = rd
        self.imm = imm

    def __repr__(self):
        return f"Instruction(opcode='{self.opcode}', rs={self.rs}, rt={self.rt}, rd={self.rd}, imm={self.imm})"

class Memory:
    def __init__(self):
        self.combined_memory = [
            # Instructions for loading matrix A and B elements into registers
            Instruction('LOAD', rs=0, rt=1, imm=0),  # Load a11 to R1
            Instruction('LOAD', rs=0, rt=2, imm=1),  # Load a12 to R2
            Instruction('LOAD', rs=0, rt=3, imm=2),  # Load a21 to R3
            Instruction('LOAD', rs=0, rt=4, imm=3),  # Load a22 to R4
            Instruction('LOAD', rs=0, rt=5, imm=4),  # Load b11 to R5
            Instruction('LOAD', rs=0, rt=6, imm=5),  # Load b12 to R6
            Instruction('LOAD', rs=0, rt=7, imm=6),  # Load b21 to R7
            Instruction('LOAD', rs=0, rt=8, imm=7),  # Load b22 to R8

            # Instructions for matrix multiplication
            # C[0][0] = a11*b11 + a12*b21
            Instruction('MUL', rs=1, rt=5, rd=9),  # R9 = R1 * R5 (a11 * b11)
            Instruction('MUL', rs=2, rt=7, rd=10), # R10 = R2 * R7 (a12 * b21)
            Instruction('ADD', rs=9, rt=10, rd=11),# R11 = R9 + R10 (C[0][0])

            # C[0][1] = a11*b12 + a12*b22
            Instruction('MUL', rs=1, rt=6, rd=12), # R12 = R1 * R6 (a11 * b12)
            Instruction('MUL', rs=2, rt=8, rd=13), # R13 = R2 * R8 (a12 * b22)
            Instruction('ADD', rs=12, rt=13, rd=14),# R14 = R12 + R13 (C[0][1])

            # C[1][0] = a21*b11 + a22*b21
            Instruction('MUL', rs=3, rt=5, rd=15), # R15 = R3 * R5 (a21 * b11)
            Instruction('MUL', rs=4, rt=7, rd=16), # R16 = R4 * R7 (a22 * b21)
            Instruction('ADD', rs=15, rt=16, rd=17),# R17 = R15 + R16 (C[1][0])

            # C[1][1] = a21*b12 + a22*b22
            Instruction('MUL', rs=3, rt=6, rd=18), # R18 = R3 * R6 (a21 * b12)
            Instruction('MUL', rs=4, rt=8, rd=19), # R19 = R4 * R8 (a22 * b22)
            Instruction('ADD', rs=18, rt=19, rd=20),# R20 = R18 + R19 (C[1][1])

            # Store results back to memory
            Instruction('STORE', rs=0, rt=11, imm=8), # Store C[0][0] in memory[8]
            Instruction('STORE', rs=0, rt=14, imm=9), # Store C[0][1] in memory[9]
            Instruction('STORE', rs=0, rt=17, imm=10),# Store C[1][0] in memory[10]
            Instruction('STORE', rs=0, rt=20, imm=11),# Store C[1][1] in memory[11]

            # Data for matrices A and B
            1, 2, # Matrix A
            3, 4, # Matrix A
            5, 6, # Matrix B
            7, 8  # Matrix B
        ]

# Example of how to use the Memory class
memory = Memory()
for instruction in memory.combined_memory:
    print(instruction)
