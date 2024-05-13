module WriteToMaster(
    input SCLK,
    input CS,
	 input reg [7:0] miso,
    output reg MISO
    
);
reg [7:0] bits;

assign bits[7] = miso[0];
assign bits[6] = miso[1];
assign bits[5] = miso[2];
assign bits[4] = miso[3];
assign bits[3] = miso[4];
assign bits[2] = miso[5];
assign bits[1] = miso[6];
assign bits[0] = miso[7];

reg [2:0] counter = 3'b000;


always @ (posedge SCLK & CS) begin
		MISO <= miso[counter];
		counter<=counter+3'b001;
end 

endmodule