module PWM_module (
	input [3:0] Porcentaje,
	input SLK,
   output reg pwm
   
);



reg [3:0] counter; //0-9


reg [3:0] mappedInput;

initial begin
		counter <= 4'b0;
end




	always @ (posedge SLK) begin
		
		mappedInput <= Porcentaje;
		
		pwm <= mappedInput > counter;
		
		counter <= counter + 4'b0001;
      
   end 
	
	

endmodule 