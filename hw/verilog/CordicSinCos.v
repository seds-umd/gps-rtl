`timescale 1ns/1ps

module CordicSinCos (
    input aclk,
    input aresetn,

    input s_axis_phase_tvalid,
    output s_axis_phase_tready,
    input [2:0] s_axis_phase_tuser,
    input [15:0] s_axis_phase_tdata,

    output m_axis_dout_tvalid,
    input m_axis_dout_tready,
    output [2:0] m_axis_dout_tuser,
    output [31:0] m_axis_dout_tdata
);

endmodule
