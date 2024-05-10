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
	output logic LED_handshake,
	);
	
	reg [3:0] A;
	reg [3:0] B;
	reg [1:0] op;
	
	reg [3:0] result;
	reg [3:0] SPI_result;
	
	reg [7:0] mosi;
	reg [7:0] miso;
	
	
	// Instancia del módulo SPI_Communication
	SPI_Communication spi_communication (
		 .CS(CS),
		 .MOSI(MOSI),
		 .SLCK(SLCK),
		 .miso(miso),
		 .mosi(mosi),
		 .num1(A), // Conecta los bits de display para num1
		 .num2(B), // Conecta los bits de display para num2
		 .operacion(op), // Conecta los bits de display para operacion
		 .resultado(SPI_result), // Conecta las señales de resultado 
		 .LED_handshake(LED_handshake)
	);
	
	WriteToMaster wtm(.SCLK(SLCK), .CS(CS), .miso(miso), .MISO(MISO)); 
	
	ALU alu1 (.A(A), .B(B), .opcode(op), .result(result), .N(N), .V(V), .Z(Z), .C(C));
	
	PWM_module pwm1(.Porcentaje(result), .SLK(SLCK), .pwm(speed));
	
	bin_to_bcd bdc1(.A(result[3]), .B(result[2]), .C(result[1]), .D(result[0]), .display(display));
	
	bin_to_bcd bdc2(.A(A[3]), .B(A[2]), .C(A[1]), .D(A[0]), .display(num1));
	
	bin_to_bcd bdc3(.A(B[7]), .B(B[6]), .C(B[5]), .D(B[4]), .display(num2));
	
	always @ (posedge SLCK & !CS) begin
    mosi[7] <= mosi[6];
    mosi[6] <= mosi[5];
    mosi[5] <= mosi[4];
    mosi[4] <= mosi[3];
    mosi[3] <= mosi[2];
    mosi[2] <= mosi[1];
    mosi[1] <= mosi[0];
    mosi[0] <= MOSI;
    
end


endmodule 