void setup() {
  Serial.begin(9600); // Iniciar comunicación serie
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
}

void loop() {
  // Leer bits para el primer número
  int num1 = digitalRead(2) | (digitalRead(3) << 1) | (digitalRead(4) << 2) | (digitalRead(5) << 3);
  // Leer bits para el segundo número
  int num2 = digitalRead(6) | (digitalRead(7) << 1) | (digitalRead(8) << 2) | (digitalRead(9) << 3);
  // Leer bits para la operación
  int operacion = digitalRead(A1) | (digitalRead(A0) << 1); // Concatenar los bits de A0 y A1 para obtener la operación

  // Realizar la operación correspondiente
  int resultado;
  switch (operacion) {
    case 0: // Suma
      resultado = num1 + num2;
      Serial.print(num1);
      Serial.print(" + ");
      Serial.print(num2);
      Serial.print(" = ");
      Serial.println(resultado);
      break;
    case 1: // Resta
      resultado = num1 - num2;
      Serial.print(num1);
      Serial.print(" - ");
      Serial.print(num2);
      Serial.print(" = ");
      Serial.println(resultado);
      break;
    case 2: // AND
      resultado = num1 & num2;
      Serial.print(num1);
      Serial.print(" AND ");
      Serial.print(num2);
      Serial.print(" = ");
      Serial.println(resultado);
      break;
    case 3: // OR
      resultado = num1 | num2;
      Serial.print(num1);
      Serial.print(" OR ");
      Serial.print(num2);
      Serial.print(" = ");
      Serial.println(resultado);
      break;
    default:
      Serial.println("Operación no válida");
  }

  delay(1000); // Esperar un segundo antes de leer nuevamente
}