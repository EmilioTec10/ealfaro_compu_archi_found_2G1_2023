//`timescale 1ns/1ps

module motor_control_tb;

    // Testbench signals
    logic clk;
    logic rst;
    logic [3:0] hex_speed;
    logic pwm;

    // Instantiate the module
    motor_control motor_control_inst(
       .clk(clk),
       .rst(rst),
       .hex_speed(hex_speed),
       .pwm(pwm)
    );

    // Clock generation
    always #10 clk = ~clk; // Generate a clock with a period of 20 ns

    // Testbench initial block
    initial begin
        // Initialize signals
        clk = 0;
        rst = 1; // Assert reset
        hex_speed = 0;
        #100; // Wait for some time
        rst = 0; // Deassert reset

        // Initialize inputs
        hex_speed = 4'h0; // Start with the motor stopped
        #200; // Wait for a while to observe the PWM output

        // Test different speed values
        hex_speed = 4'h1; // Minimum speed
        #200; // Wait to observe the PWM output

        hex_speed = 4'h3; // Low speed
        #200; // Wait to observe the PWM output

        hex_speed = 4'h8; // Medium speed
        #200; // Wait to observe the PWM output

        hex_speed = 4'hC; // High speed
        #200; // Wait to observe the PWM output

        hex_speed = 4'hF; // Maximum speed
        #200; // Wait to observe the PWM output

        // Finish the simulation
        #1000; // Run the simulation for 1 us
        $finish;
    end

    // Monitor changes in the PWM output
    initial begin
        $monitor("Time: %t, hex_speed: %h, PWM: %b", $time, hex_speed, pwm);
    end

endmodule