class ALU:
    def __init__(self):
        pass

    def operacion(self, opcode, operandos):
        if opcode == 'ADD':
            return operandos[0] + operandos[1]
        elif opcode == 'SUB':
            return operandos[0] - operandos[1]
        elif opcode == 'MUL':
            return operandos[0] * operandos[1]
        elif opcode == 'DIV':
            if operandos[1] != 0:
                return operandos[0] / operandos[1]
            else:
                return None  # Manejo de división por cero
        else:
            return None  # Operación no soportada

class DataMemory:
    def __init__(self):
        self.data = [0] * 256  # Memoria de datos con tamaño suficiente para el ejemplo

    def store(self, direccion, valor):
        self.data[direccion] = valor

    def load(self, direccion):
        return self.data[direccion]

class SegmentadoProcessor:
    def __init__(self):
        self.registros = [0] * 8  # Registros simulados (R0-R7)
        self.dm = DataMemory()  # Memoria de datos
        self.pc = 0  # Contador de programa
        self.pipeline = [{'etapa': 'Fetch', 'instruccion': None},
                         {'etapa': 'Decode', 'instruccion': None},
                         {'etapa': 'Execute', 'instruccion': None}]  # Pipeline con etapas y estado de instrucción
        self.cycle = 0  # Ciclo actual
        self.alu = ALU()  # Instancia de la ALU

    def fetch(self):
        # Simulación de Fetch: obtiene la instrucción en PC actual desde la memoria de programa
        if self.pc < len(self.programa):
            instruccion = self.programa[self.pc]
            return instruccion
        else:
            return None

    def decode(self, instruccion):
        # Simulación de Decode: decodifica la instrucción
        if instruccion is not None:
            opcode = instruccion[:6]
            operandos = [int(instruccion[6:8], 2), int(instruccion[8:], 2)]  # Decodificación básica de operandos
            reg_dest = (operandos[0] + 4) % len(self.registros)  # Dirección de registro destino
            return {'opcode': opcode, 'operandos': operandos, 'reg_dest': reg_dest}
        else:
            return None

    def execute(self, instruccion):
        # Simulación de Execute: realiza la operación utilizando la ALU
        if instruccion is not None:
            opcode = instruccion['opcode']
            operandos = instruccion['operandos']
            if opcode == '110101':  # MUL
                resultado = self.alu.operacion('MUL', operandos)
                return {'reg_dest': instruccion['reg_dest'], 'resultado': resultado}
            elif opcode == '000111':  # ADD
                resultado = self.alu.operacion('ADD', operandos)
                return {'reg_dest': instruccion['reg_dest'], 'resultado': resultado}
            elif opcode == '111111':  # STORE
                direccion = operandos[0]
                valor = operandos[1]
                self.dm.store(direccion, valor)
                return None  # No se necesita actualizar el pipeline
            elif opcode == '100001':  # LOAD
                direccion = operandos[1]
                valor = self.dm.load(direccion)
                return {'reg_dest': instruccion['reg_dest'], 'resultado': valor}
            else:
                return None  # Instrucción no soportada
        else:
            return None

    def step(self):
        # Avance de un ciclo en el pipeline
        for i in range(len(self.pipeline) - 1, -1, -1):
            etapa = self.pipeline[i]['etapa']
            instruccion = self.pipeline[i]['instruccion']

            if etapa == 'Execute' and instruccion is not None:
                resultado = self.execute(instruccion)
                if resultado is not None:
                    self.pipeline[i]['instruccion'] = resultado

            if etapa == 'Fetch' and (i == 0 or self.pipeline[i - 1]['etapa'] == 'Decode'):
                self.pipeline[i]['instruccion'] = self.fetch()

            elif etapa == 'Decode' and (i == len(self.pipeline) - 1 or self.pipeline[i + 1]['etapa'] == 'Fetch'):
                instruccion = self.decode(self.pipeline[i]['instruccion'])
                if instruccion is not None:
                    self.pipeline[i]['instruccion'] = instruccion  # Almacenar la instrucción decodificada

        self.pc += 1
        self.cycle += 1

    def run(self, programa):
        # Ejecución completa del programa
        self.programa = programa
        while self.pc < len(self.programa):
            self.step()
            self.imprimir_estado()  # Imprimir estado después de cada ciclo

    def imprimir_estado(self):
        print(f"Ciclo actual: {self.cycle}")
        print(f"PC: {self.pc}")
        print(f"Registros: {self.registros}")
        print(f"Memoria de Datos:")
        for i, valor in enumerate(self.dm.data):
            print(f"  Memoria[{i}]: {valor}")

# Definir las matrices de ejemplo
matrix_a = [
    [1, 2],
    [3, 4]
]

matrix_b = [
    [5, 6],
    [7, 8]
]

# Inicializar el procesador segmentado
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
instructions = [
    # Calcular C[0][0]
    '10000100',  # LOAD R1, 0(R0)  -> Cargar A[0][0] en R1
    '10010101',  # LOAD R2, 4(R0)  -> Cargar B[0][0] en R2
    '11010100',  # MUL R3, R1, R2  -> Multiplicar R1 y R2 y almacenar en R3
    '10000101',  # LOAD R1, 1(R0)  -> Cargar A[0][1] en R1
    '10010111',  # LOAD R2, 5(R0)  -> Cargar B[1][0] en R2
    '11010100',  # MUL R4, R1, R2  -> Multiplicar R1 y R2 y almacenar en R4
    '00011101',  # ADD R3, R3, R4  -> Sumar R3 y R4 y almacenar en R3
    '11111100',  # STORE 8(R0), R3 -> Almacenar el resultado en C[0][0]

    # Calcular C[0][1]
    '10000100',  # LOAD R1, 0(R0)  -> Cargar A[0][0] en R1
    '10010110',  # LOAD R2, 6(R0)  -> Cargar B[0][1] en R2
    '11010100',  # MUL R3, R1, R2  -> Multiplicar R1 y R2 y almacenar en R3
    '10000101',  # LOAD R1, 1(R0)  -> Cargar A[0][1] en R1
    '10010111',  # LOAD R2, 7(R0)  -> Cargar B[1][1] en R2
    '11010100',  # MUL R4, R1, R2  -> Multiplicar R1 y R2 y almacenar en R4
    '00011101',  # ADD R3, R3, R4  -> Sumar R3 y R4 y almacenar en R3
    '11111101',  # STORE 9(R0), R3 -> Almacenar el resultado en C[0][1]

    # Calcular C[1][0]
    '10000110',  # LOAD R1, 2(R0) # Continuación de definición de instrucciones para el producto de matrices
    '10000100',  # LOAD R1, 0(R0)  -> Cargar A[0][0] en R1
    '10011000',  # LOAD R2, 8(R0)  -> Cargar C[0][0] en R2
    '11010100',  # MUL R3, R1, R2  -> Multiplicar R1 y R2 y almacenar en R3
    '10000101',  # LOAD R1, 1(R0)  -> Cargar A[0][1] en R1
    '10011001',  # LOAD R2, 9(R0)  -> Cargar C[0][1] en R2
    '11010100',  # MUL R4, R1, R2  -> Multiplicar R1 y R2 y almacenar en R4
    '00011101',  # ADD R3, R3, R4  -> Sumar R3 y R4 y almacenar en R3
    '11111110',  # STORE 10(R0), R3 -> Almacenar el resultado en C[1][0]

    # Calcular C[1][1]
    '10000110',  # LOAD R1, 2(R0)  -> Cargar A[1][0] en R1
    '10011002',  # LOAD R2, 10(R0) -> Cargar C[1][0] en R2
    '11010100',  # MUL R3, R1, R2  -> Multiplicar R1 y R2 y almacenar en R3
    '10000111',  # LOAD R1, 3(R0)  -> Cargar A[1][1] en R1
    '10011003',  # LOAD R2, 11(R0) -> Cargar C[1][1] en R2
    '11010100',  # MUL R4, R1, R2  -> Multiplicar R1 y R2 y almacenar en R4
    '00011101',  # ADD R3, R3, R4  -> Sumar R3 y R4 y almacenar en R3
    '11111111',  # STORE 11(R0), R3 -> Almacenar el resultado en C[1][1]
]

# Ejecutar el programa de instrucciones
processor.run(instructions)
processor.imprimir_estado()
