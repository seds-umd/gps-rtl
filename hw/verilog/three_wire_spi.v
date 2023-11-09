module three_wire_spi 
#(
    parameter div=100,
    parameter reg0=28'hA2951A3, // Config 1
    parameter reg1=28'h8550488, // Config 2
    parameter reg2=28'hE6FFDF2, // Config 3
    parameter reg3=28'h9EC0008, // PLL Config
    parameter reg4=28'h00C0008, // PLL integer division ratio
    parameter reg5=28'h4000070, // PLL fractional division ratio
    parameter reg6=28'h8000000, // Reserved
    parameter reg7=28'h10061B6  // Clock fractional division ratio
)
(
    input wire clk, rst,
    output SCLK, 
    output reg CS, SDATA
);

reg clk_en = 0; 

reg [7:0] clk_cnt = 0;
reg [3:0] reg_cnt = 0;
reg [6:0] b_cnt = 0;

assign SCLK = (clk_cnt > (div >> 1)) & (b_cnt > 1) & (clk_cnt != 0);

always @(posedge clk)
    if (rst) begin
        clk_cnt <= 0;
        clk_en <= 0;
    end
    else if (clk_cnt == div) begin
        clk_cnt <= 0;
        clk_en <= 1;
    end else begin
        clk_cnt <= clk_cnt + 1;
        clk_en <= 0;
    end

always @(posedge clk)
    if (rst) begin
        b_cnt <= 0;
        CS <= 1;
        reg_cnt <= 0;
    end
    else if (clk_en == 1 && (reg_cnt < 8)) begin
        if (b_cnt == 33) begin
            b_cnt <= 0;
            CS <= 1;
            reg_cnt <= reg_cnt + 1;
        end
        else begin
            CS <= 0;
            b_cnt <= b_cnt + 1;
        end
    end

always @(*)
    if (b_cnt <= 29 & b_cnt > 1) begin
        case (reg_cnt)
            0: SDATA = reg0[29 - b_cnt[5:0]];
            1: SDATA = reg1[29 - b_cnt[5:0]];
            2: SDATA = reg2[29 - b_cnt[5:0]];
            3: SDATA = reg3[29 - b_cnt[5:0]];
            4: SDATA = reg4[29 - b_cnt[5:0]];
            5: SDATA = reg5[29 - b_cnt[5:0]];
            6: SDATA = reg6[29 - b_cnt[5:0]];
            7: SDATA = reg7[29 - b_cnt[5:0]];
            default: SDATA = 0;
        endcase
    end
    else if (b_cnt > 29)
        SDATA = reg_cnt[33-b_cnt[5:0]];
    else begin
        SDATA = 0;
    end

endmodule
