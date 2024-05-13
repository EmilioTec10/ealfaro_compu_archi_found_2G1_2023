#include <SPI.h>

const int CS_PIN = 10; // Pin para Chip Select (CS)
const int MOSI_PIN = 11; // Pin MOSI
const int MISO_PIN = 12; // Pin MISO
const int SCLK_PIN = 13; // Pin SCLK

bool handshake_accepted;

bool confirmHandshake() {
  // Realizar handshake enviando el mensaje de handshake
  digitalWrite(CS_PIN, LOW); // Activar dispositivo SPI
  SPI.transfer(0xAA); // Mensaje de handshake
  Serial.println("Se mando el dato para iniciar el handshake");
  digitalWrite(CS_PIN, HIGH); // Desactivar dispositivo SPI

  // Esperar a que el dispositivo receptor esté listo
  delay(100); // Ajustar el tiempo según sea necesario

  // Leer la respuesta de la FPGA
  digitalWrite(CS_PIN, LOW); // Activar dispositivo SPI
  byte response = SPI.transfer(0x00); // Leer la respuesta de la FPGA
  Serial.print("Respuesta hexadecimal: 0x");
  Serial.println(response, HEX); // Imprimir la respuesta como un número hexadecimal
  digitalWrite(CS_PIN, HIGH); // Desactivar dispositivo SPI

  // Si la respuesta es la esperada, retornar true, en caso contrario, false
  return (response == 0xBB);
}

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
  SPI.beginTransaction(SPISettings(2000000, MSBFIRST, SPI_MODE0)); // Reloj de 2 MHz, MSB first, mode 0
  pinMode(CS_PIN, OUTPUT); // Configurar CS_PIN como salida
  handshake_accepted = confirmHandshake();
}

void loop() {
  

  if (handshake_accepted) {
    Serial.println("Conexion establecida correctamente");
    // Leer bits para el primer número
    int num1 = digitalRead(2) | (digitalRead(3) << 1) | (digitalRead(4) << 2) | (digitalRead(5) << 3);
    // Leer bits para el segundo número
    int num2 = digitalRead(6) | (digitalRead(7) << 1) | (digitalRead(8) << 2) | (digitalRead(9) << 3);
    // Leer bits para la operación
    int operacion = digitalRead(A1) | (digitalRead(A0) << 1); // Concatenar los bits de A0 y A1 para obtener la operación

    SPI.setClockDivider(SPI_CLOCK_DIV128);

    digitalWrite(CS_PIN, LOW); // Activar dispositivo SPI

    // Dividir num1 en bytes y enviar cada byte
    byte num1_bytes[2];
    num1_bytes[0] = (byte)(num1 >> 8); // Byte más significativo
    num1_bytes[1] = (byte)num1;        // Byte menos significativo
    SPI.transfer(num1_bytes, 2);       // Enviar los dos bytes de num1

    // Dividir num2 en bytes y enviar cada byte
    byte num2_bytes[2];
    num2_bytes[0] = (byte)(num2 >> 8); // Byte más significativo
    num2_bytes[1] = (byte)num2;        // Byte menos significativo
    SPI.transfer(num2_bytes, 2);       // Enviar los dos bytes de num2

    // Enviar operacion
    byte operacion_byte = (byte)operacion;
    SPI.transfer(&operacion_byte, 1);  // Enviar el byte de operacion


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
  }
  delay(1000); // Esperar antes de la siguiente iteración
}
