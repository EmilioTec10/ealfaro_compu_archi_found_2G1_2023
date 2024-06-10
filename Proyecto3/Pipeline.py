import time

class InstructionMemory:
    def __init__(self, size):
        self.memory = ['00000000'] * size
    
    def loadInstructions(self, instructions):
        for i, instr in enumerate(instructions):
            self.memory[i] = instr
    
    def fetch(self, address):
        return self.memory[address]

class RegisterFile:
    def __init__(self):
        self.registers = [0] * 32
    
    def read(self, regNum):
        return self.registers[regNum]
    
    def write(self, regNum, data):
        if regNum != 0:  # El registro 0 siempre es 0
            self.registers[regNum] = data

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

class PipelineProcessor:
    def __init__(self):
        self.im = InstructionMemory(256)
        self.rf = RegisterFile()
        self.alu = ALU()
        self.dm = DataMemory(256)
        self.pc = 0
        self.cycleCount = 0
        self.startTime = None

        # Inicializar registros de pipeline
        self.ifId = None
        self.idEx = None
        self.exMem = None
        self.memWb = None
    
    def loadInstructions(self, instructions):
        self.im.loadInstructions(instructions)
    
    def executeCycle(self):
        if self.startTime is None:
            self.startTime = time.time()

        # Write-back
        if self.memWb:
            if self.memWb['writeReg'] is not None:
                self.rf.write(self.memWb['writeReg'], self.memWb['writeData'])
        
        # Memory
        if self.exMem:
            memWb = {}
            memWb['writeReg'] = self.exMem['writeReg']
            if self.exMem['memRead']:
                memWb['writeData'] = self.dm.load(self.exMem['aluResult'])
            elif self.exMem['memWrite']:
                self.dm.store(self.exMem['aluResult'], self.exMem['writeData'])
                memWb['writeData'] = None
            else:
                memWb['writeData'] = self.exMem['aluResult']
            self.memWb = memWb
        
        # Execute
        if self.idEx:
            exMem = {}
            exMem['writeReg'] = self.idEx['writeReg']
            operand1 = self.idEx['operand1']
            operand2 = self.idEx['operand2']
            exMem['aluResult'] = self.alu.execute(self.idEx['aluOp'], operand1, operand2)
            exMem['memRead'] = self.idEx['memRead']
            exMem['memWrite'] = self.idEx['memWrite']
            exMem['writeData'] = self.idEx['operand2']
            self.exMem = exMem
        
        # Decode
        if self.ifId:
            idEx = {}
            instruction = self.ifId['instruction']
            opcode = instruction[0:2]
            rs = int(instruction[2:4], 2)
            rt = int(instruction[4:6], 2)
            rd = int(instruction[6:8], 2)

            idEx['writeReg'] = rd
            idEx['operand1'] = self.rf.read(rs)
            idEx['operand2'] = self.rf.read(rt)
            if opcode == '00':  # ADD
                idEx['aluOp'] = 'ADD'
                idEx['memRead'] = False
                idEx['memWrite'] = False
            elif opcode == '01':  # SUB
                idEx['aluOp'] = 'SUB'
                idEx['memRead'] = False
                idEx['memWrite'] = False
            elif opcode == '10':  # LOAD
                idEx['aluOp'] = 'ADD'
                idEx['memRead'] = True
                idEx['memWrite'] = False
            elif opcode == '11':  # STORE
                idEx['aluOp'] = 'ADD'
                idEx['memRead'] = False
                idEx['memWrite'] = True
            elif opcode == '12':  # MUL
                idEx['aluOp'] = 'MUL'
                idEx['memRead'] = False
                idEx['memWrite'] = False
            self.idEx = idEx
        
        # Fetch
        instruction = self.im.fetch(self.pc)
        self.ifId = {'instruction': instruction}

        # Incrementar PC
        self.pc += 1
        self.cycleCount += 1

    def run(self, mode='complete', cycleTime=1):
        if self.startTime is None:
            self.startTime = time.time()
        
        if mode == 'step':
            while self.pc < len(self.im.memory) and self.im.memory[self.pc] != '00000000':
                self.executeCycle()
                self.printStatistics()
                input("Press Enter to execute next cycle...")
        
        elif mode == 'timed':
            while self.pc < len(self.im.memory) and self.im.memory[self.pc] != '00000000':
                self.executeCycle()
                self.printStatistics()
                time.sleep(cycleTime)
        
        elif mode == 'complete':
            while self.pc < len(self.im.memory) and self.im.memory[self.pc] != '00000000':
                self.executeCycle()
            self.printStatistics()
    
    def printStatistics(self):
        elapsedTime = time.time() - self.startTime
        print(f"Ciclo de ejecución: {self.cycleCount}")
        print(f"Tiempo desde inicio: {elapsedTime:.6f} segundos")
        print(f"Valor del PC: {self.pc}")
        print(f"Valores de los registros: {self.rf.registers}")
        print(f"Contenido de memoria desde 0 hasta la última celda:")
        for i, val in enumerate(self.dm.memory):
            print(f"Memoria[{i}] = {val}")

# Preguntar al usuario el modo de ejecución
mode = input("Seleccione el modo de ejecución (step, timed, complete): ")
cycleTime = 1
if mode == 'timed':
    cycleTime = float(input("Ingrese el tiempo por ciclo (en segundos): "))

# Inicialización del procesador y carga de instrucciones
processor = PipelineProcessor()

# Definición de matrices de ejemplo (2x2)
matrixA = [[1, 2], [3, 4]]
matrixB = [[5, 6], [7, 8]]

# Convertir las matrices en una lista lineal para almacenarlas en memoria
matrixAFlat = [elem for row in matrixA for elem in row]
matrixBFlat = [elem for row in matrixB for elem in row]

# Cargar las matrices en la memoria de datos
for i, val in enumerate(matrixAFlat):
    processor.dm.store(i, val)
for i, val in enumerate(matrixBFlat, start=len(matrixAFlat)):
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
processor.loadInstructions(instructions)
processor.run(mode, cycleTime)
processor.printStatistics()
