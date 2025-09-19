// hw/verilog/prn_loopback.v
// Simple PRN + carrier generator for demo loopback

module prn_loopback (
    input  wire clk,
    input  wire reset,
    output wire signed [7:0] if_out
);

    // -----------------------------
    // Carrier NCO (square wave)
    // -----------------------------
    reg [15:0] carrier_acc = 0;
    wire carrier;
    assign carrier = carrier_acc[15];  // MSB is our square wave

    always @(posedge clk) begin
        if (reset)
            carrier_acc <= 16'd0;
        else
            carrier_acc <= carrier_acc + 16'd512;  
        // increment sets "IF frequency"
    end

    // -----------------------------
    // PRN generator instance
    // NOTE: you already have prn_gen in repo (see hw/tb/Prn/test_prn)
    // -----------------------------
    wire prn_bit;
    prn_gen prn_inst (
        .clk(clk),
        .reset(reset),
        .prn_id(6),   // Fixed PRN for demo
        .chip(prn_bit)
    );

    // -----------------------------
    // BPSK modulated IF output
    // -----------------------------
    assign if_out = (prn_bit ^ carrier) ? 8'sd64 : -8'sd64;

endmodule
