module Slave_SPI(
	input logic CS,
	input logic MOSI,
	input logic SLCK,
	output logic MISO,
	output reg [6:0] display,
	output reg [6:0] num1,
	output reg [6:0] num2,
	output logic Z, 
	output logic C, 
	output logic V, 
	output logic N,
	output logic speed,
	output logic LED_MOSI
	);
	
	reg [3:0] A;
	reg [3:0] B;
	reg [1:0] op;
	
	reg [3:0] result;
	reg [3:0] SPI_result;
	
	
	// Instancia del módulo SPI_Communication
	SPI_Communication spi_communication (
		 .CS(CS),
		 .MOSI(MOSI),
		 .SLCK(SLCK),
		 .MISO(MISO),
		 .num1(A), // Conecta los bits de display para num1
		 .num2(B), // Conecta los bits de display para num2
		 .operacion(op), // Conecta los bits de display para operacion
		 .resultado(SPI_result) // Conecta las señales de resultado a N, V, Z, C
	);
	
	ALU alu1 (.A(A), .B(B), .opcode(op), .result(result), .N(N), .V(V), .Z(Z), .C(C));
	
	PWM_module pwm1(.Porcentaje(result), .SLK(SLCK), .pwm(speed));
	
	bin_to_bcd bdc1(.A(result[3]), .B(result[2]), .C(result[1]), .D(result[0]), .display(display));
	
	bin_to_bcd bdc2(.A(A[3]), .B(A[2]), .C(A[1]), .D(A[0]), .display(num1));
	
	bin_to_bcd bdc3(.A(B[3]), .B(B[2]), .C(B[1]), .D(B[0]), .display(num2));
	
	assign LED_MOSI = MOSI;

endmodule 