module motor_control (
    input logic clk,
    input logic rst, 
    input logic [3:0] hex_speed, // 4-bit input for hexadecimal speed value
    output logic pwm // PWM output for speed control
);

    logic [15:0] count = 0;
    logic [15:0] speed = 0;
	 
	 //the resulting PWM frequency would be 1 kHz (50,000,000 Hz / 50000)
	 //Assuming system clk of 50 MHz
	localparam FREQUENCY = 50000; 

    always_ff @(posedge clk or posedge rst) begin
        if (rst) begin
            // Reset internal state when rst is asserted
            count = 0;
            speed = 0;
            pwm = 0;
        end else begin
            // Map the 4-bit hex value to a speed value
            // Assuming a linear mapping for simplicity
            speed = hex_speed * (FREQUENCY / 15); // Scale the hex value to the PWM range

            // Counter logic
            if (count >= FREQUENCY-1) begin
                count = 0;
            end else begin
                count = count + 1;
            end

            // PWM output logic for speed control
            pwm = (count < speed) ? 1 : 0;
        end
    end

endmodule
