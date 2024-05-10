module Slave_SPI(
	input logic CS,
	input logic MOSI,
	input logic SLCK,
	output logic MISO,
	output reg [6:0] display,
	output logic Z, 
	output logic C, 
	output logic V, 
	output logic N,
	output logic speed
	);
	
	reg [3:0] A = 4'b0001;
	reg [3:0] B = 4'b0011;
	reg [1:0] op = 2'b00;
	
	reg [3:0] result;
	
	ALU alu1 (.A(A), .B(B), .opcode(op), .result(result), .N(N), .V(V), .Z(Z), .C(C));
	
	PWM_module pwm1(.Porcentaje(result), .SLK(SLCK), .pwm(speed));
	
	bin_to_bcd bdc1(.A(result[3]), .B(result[2]), .C(result[1]), .D(result[0]), .display(display));

endmodule 