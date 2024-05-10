//Half - adder -----------
module half_adder (
    input bit a,
    input bit b,
    output sum,
    output carry
);
    assign sum = a ^ b;
    assign carry = a & b;
endmodule


//Full - adder -----------
module full_adder (
    input bit a,
    input bit b,
    input bit cin,
    output sum,
    output cout
);
    wire s1, c1, c2;
    half_adder HA1(.a(a), .b(b), .sum(s1), .carry(c1));
    half_adder HA2(.a(s1), .b(cin), .sum(sum), .carry(c2));
    assign cout = c1 | c2;
endmodule


//Nbit - adder -----------
module adder_n_bit #(parameter N = 4)(
    input [N-1:0] a,
    input [N-1:0] b,
    output [N-1:0] sum,
    output cout
);
    wire [N:0] c;
    genvar i;
    generate
        for (i = 0; i < N; i = i + 1) begin : ADD_LOOP
            if (i == 0) begin
                full_adder FA1(.a(a[i]), .b(b[i]), .cin(1'b0), .sum(sum[i]), .cout(c[i]));
            end else begin
                full_adder FA(.a(a[i]), .b(b[i]), .cin(c[i-1]), .sum(sum[i]), .cout(c[i]));
            end
        end
    endgenerate
    assign cout = c[N-1];
endmodule