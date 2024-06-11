import time

class InstructionMemory:
    def __init__(self, size):
        self.memory = ['00000000'] * size
    
    def load_instructions(self, instructions):
        for i, instr in enumerate(instructions):
            self.memory[i] = instr
    
    def fetch(self, address):
        return self.memory[address]

class RegisterFile:
    def __init__(self):
        self.registers = [0] * 32
    
    def read(self, reg_num):
        return self.registers[reg_num]
    
    def write(self, reg_num, data):
        if reg_num != 0:  # El registro 0 siempre es 0
            self.registers[reg_num] = data

class ALU:
    def __init__(self):
        pass
    
    def execute(self, operation, operand1, operand2):
        if operation == 'ADD':
            return operand1 + operand2
        elif operation == 'SUB':
            return operand1 - operand2
        elif operation == 'MUL':
            return operand1 * operand2
        elif operation == 'AND':
            return operand1 & operand2
        elif operation == 'OR':
            return operand1 | operand2
        elif operation == 'SLT':  # Set on less than
            return 1 if operand1 < operand2 else 0
        else:
            raise ValueError("Operación no soportada")

class DataMemory:
    def __init__(self, size):
        self.memory = [0] * size
    
    def load(self, address):
        return self.memory[address]
    
    def store(self, address, data):
        self.memory[address] = data

class PipelineRegister:
    def __init__(self):
        self.instruction = None
        self.pc = 0
        self.alu_result = 0
        self.read_data = 0
        self.write_data = 0
        self.rs = 0
        self.rt = 0
        self.rd = 0
        self.operation = ''
        self.stage = 'IF'

class HazardUnit:
    def __init__(self):
        self.forwardA = '00'
        self.forwardB = '00'
        self.stall = False

    def detect_hazard(self, id_ex, ex_mem, mem_wb):
        self.stall = False
        self.forwardA = '00'
        self.forwardB = '00'

        # Forwarding for EX stage
        if ex_mem.rd != 0 and ex_mem.rd == id_ex.rs:
            self.forwardA = '10'
        elif mem_wb.rd != 0 and mem_wb.rd == id_ex.rs:
            self.forwardA = '01'
        
        if ex_mem.rd != 0 and ex_mem.rd == id_ex.rt:
            self.forwardB = '10'
        elif mem_wb.rd != 0 and mem_wb.rd == id_ex.rt:
            self.forwardB = '01'

        # Load-use hazard
        if id_ex.operation == 'LOAD' and (id_ex.rt == ex_mem.rs or id_ex.rt == ex_mem.rt):
            self.stall = True

class SegmentadoProcessor:
    def __init__(self):
        self.im = InstructionMemory(256)
        self.rf = RegisterFile()
        self.alu = ALU()
        self.dm = DataMemory(256)
        self.pc = 0
        self.cycle_count = 0
        self.start_time = None

        # Pipeline registers
        self.IF_ID = PipelineRegister()
        self.ID_EX = PipelineRegister()
        self.EX_MEM = PipelineRegister()
        self.MEM_WB = PipelineRegister()

        self.hazard_unit = HazardUnit()
    
    def load_instructions(self, instructions):
        self.im.load_instructions(instructions)
    
    def fetch(self):
        if self.pc < len(self.im.memory) and self.im.memory[self.pc] != '00000000':
            instruction = self.im.fetch(self.pc)
            self.IF_ID.instruction = instruction
            self.IF_ID.pc = self.pc
            self.IF_ID.stage = 'ID'
            self.pc += 1
        else:
            self.IF_ID.instruction = None

    def decode(self):
        instruction = self.IF_ID.instruction
        if instruction is not None:
            opcode = instruction[0:2]
            rs = int(instruction[2:4], 2)
            rt = int(instruction[4:6], 2)
            rd = int(instruction[6:8], 2)

            self.ID_EX.pc = self.IF_ID.pc
            self.ID_EX.rs = rs
            self.ID_EX.rt = rt
            self.ID_EX.rd = rd
            self.ID_EX.stage = 'EX'
            self.ID_EX.operation = opcode

            self.ID_EX.read_data = self.rf.read(rs)
            self.ID_EX.write_data = self.rf.read(rt)
        else:
            self.ID_EX.instruction = None
    
    def execute(self):
        if self.ID_EX.instruction is not None:
            operation = self.ID_EX.operation
            operand1 = self.ID_EX.read_data
            operand2 = self.ID_EX.write_data

            if self.hazard_unit.forwardA == '10':
                operand1 = self.EX_MEM.alu_result
            elif self.hazard_unit.forwardA == '01':
                operand1 = self.MEM_WB.alu_result

            if self.hazard_unit.forwardB == '10':
                operand2 = self.EX_MEM.alu_result
            elif self.hazard_unit.forwardB == '01':
                operand2 = self.MEM_WB.alu_result

            if operation == '00':  # ADD
                self.EX_MEM.alu_result = self.alu.execute('ADD', operand1, operand2)
            elif operation == '01':  # SUB
                self.EX_MEM.alu_result = self.alu.execute('SUB', operand1, operand2)
            elif operation == '10':  # LOAD
                self.EX_MEM.alu_result = operand1 + operand2
            elif operation == '11':  # STORE
                self.EX_MEM.alu_result = operand1 + operand2

            self.EX_MEM.stage = 'MEM'
            self.EX_MEM.rd = self.ID_EX.rd
        else:
            self.EX_MEM.instruction = None
    
    def memory(self):
        if self.EX_MEM.instruction is not None:
            if self.EX_MEM.operation == '10':  # LOAD
                self.MEM_WB.alu_result = self.dm.load(self.EX_MEM.alu_result)
            elif self.EX_MEM.operation == '11':  # STORE
                self.dm.store(self.EX_MEM.alu_result, self.rf.read(self.EX_MEM.rd))
            else:
                self.MEM_WB.alu_result = self.EX_MEM.alu_result

            self.MEM_WB.stage = 'WB'
            self.MEM_WB.rd = self.EX_MEM.rd
        else:
            self.MEM_WB.instruction = None
    
    def write_back(self):
        if self.MEM_WB.instruction is not None:
            self.rf.write(self.MEM_WB.rd, self.MEM_WB.alu_result)

    def execute_cycle(self):
        if self.start_time is None:
            self.start_time = time.time()

        # Write Back
        self.write_back()
        # Memory
        self.memory()
        # Execute
        self.execute()
        # Decode
        self.decode()
        # Fetch
        self.fetch()

        # Check hazards
        self.hazard_unit.detect_hazard(self.ID_EX, self.EX_MEM, self.MEM_WB)
        if self.hazard_unit.stall:
            self.pc -= 1  # Stall the pipeline

        self.cycle_count += 1

    def run(self, mode='complete', cycle_time=1):
        if self.start_time is None:
            self.start_time = time.time()
        
        if mode == 'step':
            while self.pc < len(self.im.memory) and self.im.memory[self.pc] != '00000000':
                self.execute_cycle()
                self.print_statistics()
                input("Press Enter to execute next cycle...")
        
        elif mode == 'timed':
            while self.pc < len(self.im.memory) and self.im.memory[self.pc] != '00000000':
                self.execute_cycle()
                self.print_statistics()
                time.sleep(cycle_time)
        
        elif mode == 'complete':
            while self.pc < len(self.im.memory) and self.im.memory[self.pc] != '00000000':
                self.execute_cycle()
            self.print_statistics()
    
    def print_statistics(self):
        elapsed_time = time.time() - self.start_time
        print(f"Ciclo de ejecución: {self.cycle_count}")
        print(f"Tiempo desde inicio: {elapsed_time:.6f} segundos")
        print(f"Valor del PC: {self.pc}")
        print(f"Valores de los registros: {self.rf.registers}")
        print(f"Contenido de memoria desde 0 hasta la última celda:")
        for i, val in enumerate(self.dm.memory):
            print(f"Memoria[{i}] = {val}")

# Preguntar al usuario el modo de ejecución
mode = input("Seleccione el modo de ejecución (step, timed, complete): ")
cycle_time = float(input("Ingrese el tiempo de ciclo en segundos (para modo timed): "))

# Definir las matrices de ejemplo
matrix_a = [
    [1, 2],
    [3, 4]
]

matrix_b = [
    [5, 6],
    [7, 8]
]

# Inicializar el procesador
processor = SegmentadoProcessor()

# Convertir matrices a una lista plana
matrix_a_flat = [elem for row in matrix_a for elem in row]
matrix_b_flat = [elem for row in matrix_b for elem in row]

# Cargar las matrices en la memoria de datos
for i, val in enumerate(matrix_a_flat):
    processor.dm.store(i, val)
for i, val in enumerate(matrix_b_flat, start=len(matrix_a_flat)):
    processor.dm.store(i, val)

# Definir instrucciones para el producto de matrices
# Suponiendo registros: 0, 1, 2, 3 para uso temporal y 4, 5 para dirección base de matrices A y B respectivamente
# Dirección base de C será el doble de la longitud de A, es decir, en posición 8
instructions = [
    # Calcular C[0][0]
    '10000100',  # LOAD R1, 0(R0)  -> Cargar A[0][0] en R1
    '10010101',  # LOAD R2, 4(R0)  -> Cargar B[0][0] en R2
    '11010110',  # MUL R3, R1, R2  -> Multiplicar R1 y R2 y almacenar en R3
    '10000101',  # LOAD R1, 1(R0)  -> Cargar A[0][1] en R1
    '10010111',  # LOAD R2, 6(R0)  -> Cargar B[1][0] en R2
    '11010110',  # MUL R3, R1, R2  -> Multiplicar R1 y R2 y almacenar en R3
    '00011110',  # ADD R3, R3, R4  -> Sumar R3 y R4 y almacenar en R3
    '10111100',  # STORE 8(R0), R3 -> Almacenar el resultado en C[0][0]

    # Calcular C[0][1]
    '10000100',  # LOAD R1, 0(R0)  -> Cargar A[0][0] en R1
    '10010110',  # LOAD R2, 5(R0)  -> Cargar B[0][1] en R2
    '11010110',  # MUL R3, R1, R2  -> Multiplicar R1 y R2 y almacenar en R3
    '10000101',  # LOAD R1, 1(R0)  -> Cargar A[0][1] en R1
    '10010111',  # LOAD R2, 7(R0)  -> Cargar B[1][1] en R2
    '11010110',  # MUL R3, R1, R2  -> Multiplicar R1 y R2 y almacenar en R3
    '00011110',  # ADD R3, R3, R4  -> Sumar R3 y R4 y almacenar en R3
    '10111101',  # STORE 9(R0), R3 -> Almacenar el resultado en C[0][1]

    # Calcular C[1][0]
    '10000110',  # LOAD R1, 2(R0)  -> Cargar A[1][0] en R1
    '10010100',  # LOAD R2, 4(R0)  -> Cargar B[0][0] en R2
    '11010110',  # MUL R3, R1, R2  -> Multiplicar R1 y R2 y almacenar en R3
    '10000111',  # LOAD R1, 3(R0)  -> Cargar A[1][1] en R1
    '10010101',  # LOAD R2, 5(R0)  -> Cargar B[0][1] en R2
    '11010110',  # MUL R3, R1, R2  -> Multiplicar R1 y R2 y almacenar en R3
    '00011110',  # ADD R3, R3, R4  -> Sumar R3 y R4 y almacenar en R3
    '10111110',  # STORE 10(R0), R3 -> Almacenar el resultado en C[1][0]

    # Calcular C[1][1]
    '10000110',  # LOAD R1, 2(R0)  -> Cargar A[1][0] en R1
    '10010110',  # LOAD R2, 6(R0)  -> Cargar B[1][0] en R2
    '11010110',  # MUL R3, R1, R2  -> Multiplicar R1 y R2 y almacenar en R3
    '10000111',  # LOAD R1, 3(R0)  -> Cargar A[1][1] en R1
    '10010111',  # LOAD R2, 7(R0)  -> Cargar B[1][1] en R2
    '11010110',  # MUL R3, R1, R2  -> Multiplicar R1 y R2 y almacenar en R3
    '00011110',  # ADD R3, R3, R4  -> Sumar R3 y R4 y almacenar en R3
    '10111111',  # STORE 11(R0), R3 -> Almacenar el resultado en C[1][1]
]

# Cargar las instrucciones y ejecutar
processor.load_instructions(instructions)
processor.run(mode, cycle_time)
processor.print_statistics()