module ALU_tb;
    logic [3:0] A, B;
    logic [1:0] opcode;
    logic [3:0] result;
    logic N, Z, C, V;

    ALU #(.WIDTH(4)) modulo(.A(A), .B(B), .opcode(opcode), .result(result),.N(N), .Z(Z), .C(C), .V(V));

    initial begin
	 
	//---------------Add------------------
		  A = 4'b1010; B = 4'b0010; opcode = 2'b00; 
		  #10
		  assert(result === 4'b1100) 
		  else $error("Adding failed");
		  A = 4'b1111; B = 4'b1111; opcode = 2'b00; 
		  #10 
		  assert(result === 4'b1110) 
		  else $error("Adding failed");
		  
	//---------------Substract------------------	  
		  A = 4'b1010; B = 4'b0010; opcode = 2'b01; 
		  #10
		  assert(result === 4'b1000) 
		  else $error("Substraction failed");
		  A = 4'b0100; B = 4'b0111; opcode = 2'b01; 
		  #10
		  assert(N === 1) 
		  else $error("Flag error");
		  
	//---------------AND------------------	  
		  A = 4'b0100; B = 4'b0011; opcode = 2'b10; 
		  #10
		  assert(result === 4'b0000) 
		  else $error("AND failed");
		  A = 4'b1111; B = 4'b1111; opcode = 2'b10; 
		  #10
		  assert(result === 4'b0010) 
		  else $error("AND failed");
		  
	//---------------OR------------------	  
		  A = 4'b0000; B = 4'b0000; opcode = 2'b11; 
		  #10
		  assert(result === 4'b1000) 
		  else $error("OR failed");
		  A = 4'b1111; B = 4'b1111; opcode = 2'b11; 
		  #10
		  assert(result === 4'b1111) 
		  else $error("OR failed");
		  
	end
endmodule