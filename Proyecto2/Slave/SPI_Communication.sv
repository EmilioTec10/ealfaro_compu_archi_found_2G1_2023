module SPI_Communication (
    input logic CS,
    input logic MOSI,
    input logic SLCK,
    output logic MISO,
    output reg [3:0] num1,
    output reg [3:0] num2,
    output reg [1:0] operacion,
    input logic [3:0] resultado
);

// FSM para manejar la recepción de datos SPI
typedef enum logic [2:0] {
    IDLE,
    RECEIVING_NUM1,
    RECEIVING_NUM2,
    RECEIVING_OPERATION
} state_t;

reg [2:0] state = IDLE;

always @(posedge SLCK) begin
    case (state)
        IDLE: begin
            if (CS == 0) begin
                state <= RECEIVING_NUM1;
            end
        end
        RECEIVING_NUM1: begin
            num1 <= {num1[2:0], MOSI};
            state <= RECEIVING_NUM2;
        end
        RECEIVING_NUM2: begin
            num2 <= {num2[2:0], MOSI};
            state <= RECEIVING_OPERATION;
        end
        RECEIVING_OPERATION: begin
            operacion <= {operacion[0], MOSI};
            state <= IDLE;
        end
        default: state <= IDLE;
    endcase
end

// Lógica para enviar el resultado a través de MISO
assign MISO = resultado[0];

endmodule
