// Blackbox module definition for Xilinx FFT core

`timescale 1ns/1ps

// verilator lint_off UNUSED
// verilator lint_off UNDRIVEN
module XilinxFFT (
    // Misc
    input aclk,
    input aresetn,
    input aclken,

    // Config
    input [7:0] s_axis_config_tdata, // bit 0: forward/inverse
    input s_axis_config_tvalid,
    output s_axis_config_tready,

    // Data input
    input [15:0] s_axis_data_tdata, // {im, re}
    input s_axis_data_tlast,
    input s_axis_data_tvalid,
    output s_axis_data_tready,

    // Data output
    output [15:0] m_axis_data_tdata, // {im, re}
    output [7:0] m_axis_data_tuser, // [4:0]: block exponent
    output m_axis_data_tlast,
    output m_axis_data_tvalid,
    input m_axis_data_tready,

    // Status
    output [7:0] m_axis_status_tdata, // [4:0]: block exponent
    output m_axis_status_tvalid,
    input m_axis_status_tready,

    // Events
    output event_frame_started,
    output event_tlast_missing,
    output event_tlast_unexpected,
    // output event_fft_overflow,
    output event_data_in_channel_halt,
    output event_data_out_channel_halt,
    output event_status_channel_halt
);

endmodule
