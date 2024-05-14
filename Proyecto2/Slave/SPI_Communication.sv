module SPI_Communication (
    input logic CS,
    input logic MOSI,
    input logic SLCK,
	 input reg [7:0] mosi,
    output reg [7:0] miso,
    output reg [3:0] num1,
    output reg [3:0] num2,
    output reg [1:0] operacion,
	 output logic LED_handshake,
    input logic [3:0] resultado
);

// FSM para manejar la recepción de datos SPI
typedef enum logic [3:0] {
    IDLE,
    RECEIVING_HANDSHAKE,
    HANDSHAKE_CONFIRMED,
    RECEIVING_NUM1,
    RECEIVING_NUM2,
    RECEIVING_OPERATION
} state_t;

reg [3:0] state = IDLE;
reg [3:0] counter;

always @(posedge SLCK) begin
    case (state)
        IDLE: begin
            if (CS == 0) begin
                state <= RECEIVING_HANDSHAKE;
            end
        end
        RECEIVING_HANDSHAKE: begin
            // Esperar el mensaje de handshake
            if (mosi == 8'hAA) begin
                state <= HANDSHAKE_CONFIRMED;
					 LED_handshake <= 1'b1;
            end
        end
        HANDSHAKE_CONFIRMED: begin
            // Confirmar el handshake enviando el valor esperado (0xBB)
            miso <= 8'hBB;
            state <= RECEIVING_NUM1;
        end
        RECEIVING_NUM1: begin
				if(counter == 3'b100)begin
					counter <= 3'b000;
					state <= RECEIVING_NUM2;
				end else begin
					num1 <= {num1[2:0], MOSI};
					counter <= counter + 3'b001;
            end
        end
        RECEIVING_NUM2: begin
            
				if(counter == 3'b100)begin
					state <= RECEIVING_OPERATION;
					counter <= 3'b000;
				end else begin
					num2 <= {num2[2:0], MOSI};
					counter <= counter + 3'b001;
				end
        end
        RECEIVING_OPERATION: begin
            operacion <= {operacion[0], MOSI};
            state <= IDLE;
        end
        default: state <= IDLE;
    endcase
end

endmodule


