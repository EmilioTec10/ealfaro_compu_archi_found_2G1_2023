module ALU #(parameter WIDTH = 4) (
    input logic [WIDTH - 1:0] A, B,
    input logic [1:0] opcode,
    output logic [WIDTH - 1:0] result,
    output logic N, Z, C, V
);

logic [WIDTH-1:0] addResult;
logic [WIDTH-1:0] subResult;
logic [WIDTH-1:0] andResult;
logic [WIDTH-1:0] orResult;

adder_n_bit #(WIDTH) adder(
    .a(A), 
    .b(B), 
    .sum(addResult), 
    .cout());

subtractor_n_bit #(WIDTH) subtractor(
    .a(A), 
    .b(B), 
    .difference(subResult), 
    .bout());

assign result = (opcode == 2'b00) ? addResult :
                (opcode == 2'b01) ? subResult :
                (opcode == 2'b10) ? andResult :
                (opcode == 2'b11) ? orResult :
                0;

assign N = (opcode == 2'b01 && (A < B));
assign Z = (result == 0);
assign C = (opcode == 2'b00) && (result < A);
assign V = (opcode == 2'b00) && (result > 0) && (result < A);

assign andResult = A & B;
assign orResult = A | B;

endmodule