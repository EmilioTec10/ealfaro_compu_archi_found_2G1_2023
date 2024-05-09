module FAC_PG1(
    input wire clk,         // Clock signal
    input wire rst,         // Reset signal
    input wire [3:0] speed, // Speed control input (4 bits for 16 speed settings)
    output wire motorSignal         // PWM output to motor
);

    // Instantiate the motor_control module
    motor_control motor_control_inst(
        .clk(clk),
        .rst(rst),
        .hex_speed(speed),
        .pwm(motorSignal)
    );

endmodule