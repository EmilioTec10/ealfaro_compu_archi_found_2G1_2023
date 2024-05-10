module PWM_module_tb;

    reg [3:0] duty_cycle;
    reg clk;
    wire pwm_out;

    // Instancia del módulo PWM
    PWM_module #(4) u1 (
        .duty_cycle(duty_cycle),
        .clk(clk),
        .pwm_out(pwm_out)
    );

    // Generador de reloj
    divideClock clk_divider (
        .clk_in(clk),
        .clk_out(clk_divided)
    );

    // Test
    initial begin
        clk = 0;
        duty_cycle = 4'h0; // Apagado
        #100;
        duty_cycle = 4'h5; // Máxima energía
        #100;
        duty_cycle = 4'hF;
		  #100;
        duty_cycle = 4'h2;
		  #100;
        duty_cycle = 4'h1;
		  #100;
        duty_cycle = 4'hA;
		  #100;
        duty_cycle = 4'h5;
		  #100
        $finish;
    end

endmodule
