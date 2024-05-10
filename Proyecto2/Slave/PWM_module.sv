module PWM_module #(parameter WIDTH = 4)
(
    input wire [WIDTH-1:0] duty_cycle,
    input wire clk,
    output reg pwm_out
);

    reg [WIDTH-1:0] counter;

    always @(posedge clk) begin
        if(counter < duty_cycle)
            pwm_out <= 1'b1;
        else
            pwm_out <= 1'b0;

        counter <= counter + 1'b1;
    end

endmodule
