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

class UnicycleProcessor:
    def __init__(self):
        self.im = InstructionMemory(256)
        self.rf = RegisterFile()
        self.alu = ALU()
        self.dm = DataMemory(256)
        self.pc = 0
        self.cycle_count = 0
        self.start_time = None
    
    def load_instructions(self, instructions):
        self.im.load_instructions(instructions)
    
    def execute_cycle(self):
        if self.start_time is None:
            self.start_time = time.time()
        
        # Fetch
        instruction = self.im.fetch(self.pc)
        
        # Decode (assuming a simple format for demonstration)
        opcode = instruction[0:2]
        rs = int(instruction[2:4], 2)
        rt = int(instruction[4:6], 2)
        rd = int(instruction[6:8], 2)
        
        # Execute
        if opcode == '00':  # ADD
            result = self.alu.execute('ADD', self.rf.read(rs), self.rf.read(rt))
            self.rf.write(rd, result)
        elif opcode == '01':  # SUB
            result = self.alu.execute('SUB', self.rf.read(rs), self.rf.read(rt))
            self.rf.write(rd, result)
        elif opcode == '10':  # LOAD
            result = self.dm.load(self.rf.read(rs) + rt)
            self.rf.write(rd, result)
        elif opcode == '11':  # STORE
            self.dm.store(self.rf.read(rs) + rt, self.rf.read(rd))
        elif opcode == '12':  # MUL
            result = self.alu.execute('MUL', self.rf.read(rs), self.rf.read(rt))
            self.rf.write(rd, result)
        
        # Increment PC
        self.pc += 1
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
cycle_time = 1
if mode == 'timed':
    cycle_time = float(input("Ingrese el tiempo por ciclo (en segundos): "))

# Inicialización del procesador y carga de instrucciones
processor = UnicycleProcessor()

# Definición de matrices de ejemplo (2x2)
matrix_a = [[1, 2], [3, 4]]
matrix_b = [[5, 6], [7, 8]]

# Convertir las matrices en una lista lineal para almacenarlas en memoria
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
