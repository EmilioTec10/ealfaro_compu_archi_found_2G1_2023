module bin_to_bcd(input A, B, C, D, output [6:0] display);
	
    assign display[0] = ~(~A & ~B & ~C & D | ~A & B & ~C & ~D | A & ~B & C & D | A & B & ~C & D); 
    assign display[1] = ~(B & C & ~D | A & C & D | A & B & ~D | ~A & B & ~C & D);
    assign display[2] = B | ~C | D | A & C; 
    assign display[3] = ~(~B & ~C & D | B & C & D | ~A & B & ~C & ~D | A & ~B & C & ~D); 
    assign display[4] = ~(~A & D | ~B & ~C & D | ~A & B & ~C); 
    assign display[5] = ~(~A & ~B & D | ~A & ~B & C | ~A & C & D | A & B & ~C & D); 
    assign display[6] = ~(~A & ~B & ~C | ~A & B & C & D | A & B & ~C & ~D); 

endmodule
