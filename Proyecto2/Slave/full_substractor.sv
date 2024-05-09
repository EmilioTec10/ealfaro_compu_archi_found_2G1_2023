module half_subtractor (
    input bit a,
    input bit b,
    output difference,
    output borrow
);
    assign difference = a ^ b;
    assign borrow = (~a) & b;
endmodule


//Full - subtractor -----------
module full_subtractor (
    input bit a,
    input bit b,
    input bit bin,
    output difference,
    output bout
);
    wire d1, b1, b2;
    half_subtractor HS1(.a(a), .b(b), .difference(d1), .borrow(b1));
    half_subtractor HS2(.a(d1), .b(bin), .difference(difference), .borrow(b2));
    assign bout = b1 | b2;
endmodule


//Nbit - subtractor -----------
module subtractor_n_bit #(parameter N = 4)(
    input [N-1:0] a,
    input [N-1:0] b,
    output [N-1:0] difference,
    output bout
);
    wire [N:0] b_;
    genvar i;
    generate
        for (i = 0; i < N; i = i + 1) begin : SUB_LOOP
            if (i == 0) begin
                full_subtractor FS1(.a(a[i]), .b(b[i]), .bin(1'b0), .difference(difference[i]), .bout(b_[i]));
            end else begin
                full_subtractor FS(.a(a[i]), .b(b[i]), .bin(b_[i-1]), .difference(difference[i]), .bout(b_[i]));
            end
        end
    endgenerate
    assign bout = b_[N-1];
endmodule