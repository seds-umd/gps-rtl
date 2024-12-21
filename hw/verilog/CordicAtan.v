`timescale 1ns/1ps

module CordicAtan (
    input aclk,
    input aresetn,

    input s_axis_cartesian_tvalid,
    output s_axis_cartesian_tready,
    input [2:0] s_axis_cartesian_tuser,
    input [31:0] s_axis_cartesian_tdata,

    output m_axis_dout_tvalid,
    input m_axis_dout_tready,
    output [2:0] m_axis_dout_tuser,
    output [15:0] m_axis_dout_tdata
);

endmodule
