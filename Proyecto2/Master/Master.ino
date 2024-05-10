#include <SPI.h>

const int CS_PIN = 10; // Pin para Chip Select (CS)
const int MOSI_PIN = 11; // Pin MOSI
const int MISO_PIN = 12; // Pin MISO
const int SCLK_PIN = 13; // Pin SCLK

void setup() {
  Serial.begin(9600); // Inicializar comunicación serial para depuración
  pinMode(A0, INPUT); // Configurar A0 como entrada
  pinMode(A1, INPUT); // Configurar A1 como entrada
  pinMode(2, INPUT);
  pinMode(3, INPUT);
  pinMode(4, INPUT);
  pinMode(5, INPUT);
  pinMode(6, INPUT);
  pinMode(7, INPUT);
  pinMode(8, INPUT);
  pinMode(9, INPUT);
  SPI.begin(); // Inicializar comunicación SPI
  pinMode(CS_PIN, OUTPUT); // Configurar CS_PIN como salida
}

void loop() {
    // Leer bits para el primer número
  int num1 = digitalRead(2) | (digitalRead(3) << 1) | (digitalRead(4) << 2) | (digitalRead(5) << 3);
  // Leer bits para el segundo número
  int num2 = digitalRead(6) | (digitalRead(7) << 1) | (digitalRead(8) << 2) | (digitalRead(9) << 3);
  // Leer bits para la operación
  int operacion = digitalRead(A1) | (digitalRead(A0) << 1); // Concatenar los bits de A0 y A1 para obtener la operación

  SPI.setClockDivider(SPI_CLOCK_DIV128);

  digitalWrite(CS_PIN, LOW); // Activar dispositivo SPI

  // Enviar num1
  for (int i = sizeof(num1) - 1; i >= 0; i--) {
    SPI.transfer((byte)(num1 >> (8 * i))); // Envía el byte i-ésimo de num1
  }

  // Enviar num2
  for (int i = sizeof(num2) - 1; i >= 0; i--) {
    SPI.transfer((byte)(num2 >> (8 * i))); // Envía el byte i-ésimo de num2
  }

  // Enviar operacion
  SPI.transfer((byte)operacion);   // Envía el byte de la operación


  Serial.println(num1);
  Serial.println(num2);
  Serial.println(operacion);

  delay(2000); // Esperar procesamiento en el módulo SystemVerilog

  // Leer resultado devuelto por el módulo SystemVerilog
  int resultado = SPI.transfer(0);

  digitalWrite(CS_PIN, HIGH); // Desactivar dispositivo SPI

  // Imprimir resultado según operación
  // switch (operacion) {
  //   case 0: // Suma
  //     Serial.print(num1);
  //     Serial.print(" + ");
  //     Serial.print(num2);
  //     Serial.print(" = ");
  //     Serial.println(resultado);
  //     break;
  //   case 1: // Resta
  //     Serial.print(num1);
  //     Serial.print(" - ");
  //     Serial.print(num2);
  //     Serial.print(" = ");
  //     Serial.println(resultado);
  //     break;
  //   case 2: // AND
  //     Serial.print(num1);
  //     Serial.print(" AND ");
  //     Serial.print(num2);
  //     Serial.print(" = ");
  //     Serial.println(resultado);
  //     break;
  //   case 3: // OR
  //     Serial.print(num1);
  //     Serial.print(" OR ");
  //     Serial.print(num2);
  //     Serial.print(" = ");
  //     Serial.println(resultado);
  //     break;
  //   default:
  //     Serial.println("Operación no válida");
  // }

  delay(1000); // Esperar antes de la siguiente iteración
}
