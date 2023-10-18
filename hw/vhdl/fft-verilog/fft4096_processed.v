module sr_unsigned_4_2
  (input  clk,
   input  [3:0] din,
   input  ce,
   output [3:0] dout);
  wire [11:0] arr;
  wire [3:0] n2237_o;
  wire n2238_o;
  wire n2239_o;
  wire [3:0] n2240_o;
  wire [3:0] n2241_o;
  wire [3:0] n2242_o;
  wire n2243_o;
  wire n2244_o;
  wire [3:0] n2245_o;
  wire [3:0] n2246_o;
  wire [3:0] n2247_o;
  wire [11:0] n2248_o;
  assign dout = n2247_o;
  /* ../fpga-fft/rtl/sr.vhd:43:16  */
  assign arr = n2248_o; // (signal)
  /* ../fpga-fft/rtl/sr.vhd:46:30  */
  assign n2237_o = arr[7:4];
  /* ../fpga-fft/rtl/sr.vhd:46:52  */
  assign n2238_o = 1'b0; // posedge
  /* ../fpga-fft/rtl/sr.vhd:46:48  */
  assign n2239_o = ce & n2238_o;
  /* ../fpga-fft/rtl/sr.vhd:46:36  */
  assign n2240_o = n2239_o ? n2237_o : n2241_o;
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:69:9  */
  assign n2241_o = arr[3:0];
  /* ../fpga-fft/rtl/sr.vhd:46:30  */
  assign n2242_o = arr[11:8];
  /* ../fpga-fft/rtl/sr.vhd:46:52  */
  assign n2243_o = 1'b0; // posedge
  /* ../fpga-fft/rtl/sr.vhd:46:48  */
  assign n2244_o = ce & n2243_o;
  /* ../fpga-fft/rtl/sr.vhd:46:36  */
  assign n2245_o = n2244_o ? n2242_o : n2246_o;
  /* ../fpga-fft/rtl/fft_types.vhd:52:14  */
  assign n2246_o = arr[7:4];
  /* ../fpga-fft/rtl/sr.vhd:49:20  */
  assign n2247_o = arr[3:0];
  assign n2248_o = {din, n2245_o, n2240_o};
endmodule

module complexramlut_8_4
  (input  rdclk,
   input  wrclk,
   input  [3:0] rdaddr,
   input  wren,
   input  [3:0] wraddr,
   input  [47:0] wrdata_re,
   input  [47:0] wrdata_im,
   output [47:0] rddata_re,
   output [47:0] rddata_im);
  wire [47:0] n2180_o;
  wire [47:0] n2181_o;
  wire [95:0] n2182_o;
  wire [3:0] rdaddr1;
  wire [15:0] wrdata1;
  wire [15:0] tmpdata;
  reg [7:0] tmpdata1 = 0;
  reg [7:0] tmpdata2 = 0;
  wire [7:0] n2190_o;
  wire [7:0] n2193_o;
  wire [47:0] n2202_o;
  wire [47:0] n2205_o;
  wire [95:0] n2206_o;
  wire [7:0] n2212_o;
  wire [7:0] n2218_o;
  wire [15:0] n2219_o;
  reg [3:0] n2231_q = 0;
  reg [7:0] n2232_q = 0;
  reg [7:0] n2233_q = 0;
  wire [15:0] n2234_data; // mem_rd
  assign rddata_re = n2180_o;
  assign rddata_im = n2181_o;
  assign n2180_o = n2206_o[47:0];
  assign n2181_o = n2206_o[95:48];
  assign n2182_o = {wrdata_im, wrdata_re};
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:41:16  */
  assign rdaddr1 = n2231_q; // (signal)
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:42:16  */
  assign wrdata1 = n2219_o; // (signal)
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:44:16  */
  assign tmpdata = n2234_data; // (signal)
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:45:16  */
  always @*
    tmpdata1 = n2232_q; // (isignal)
  initial
    tmpdata1 = 8'b00000000;
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:45:25  */
  always @*
    tmpdata2 = n2233_q; // (isignal)
  initial
    tmpdata2 = 8'b00000000;
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:60:35  */
  assign n2190_o = tmpdata[7:0];
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:61:35  */
  assign n2193_o = tmpdata[15:8];
  /* ../fpga-fft/rtl/fft_types.vhd:139:27  */
  assign n2202_o = {{40{tmpdata1[7]}}, tmpdata1}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:140:27  */
  assign n2205_o = {{40{tmpdata2[7]}}, tmpdata2}; // sext
  assign n2206_o = {n2205_o, n2202_o};
  /* ../fpga-fft/rtl/fft_types.vhd:150:30  */
  assign n2212_o = n2182_o[55:48];
  /* ../fpga-fft/rtl/fft_types.vhd:146:30  */
  assign n2218_o = n2182_o[7:0];
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:67:25  */
  assign n2219_o = {n2212_o, n2218_o};
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:54:27  */
  always @(posedge rdclk)
    n2231_q <= rdaddr;
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:60:58  */
  always @(posedge rdclk)
    n2232_q <= n2190_o;
  initial
    n2232_q = 8'b00000000;
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:61:62  */
  always @(posedge rdclk)
    n2233_q <= n2193_o;
  initial
    n2233_q = 8'b00000000;
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:24:25  */
  reg [15:0] ram1[15:0] ; // memor = 0;
  assign n2234_data = ram1[rdaddr1];
  always @(posedge wrclk)
    if (wren)
      ram1[wraddr] <= wrdata1;
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:58:25  */
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:73:46  */
endmodule

module transposer_addrgen_2_2_2
  (input  clk,
   input  reorderenable,
   input  [3:0] phase,
   output [3:0] addr);
  wire [3:0] ph1;
  wire [3:0] ph2;
  wire [3:0] ph3;
  reg [1:0] state = 0;
  reg [1:0] statenext = 0;
  wire [3:0] n2143_o;
  wire [3:0] n2145_o;
  wire [1:0] n2151_o;
  wire [1:0] n2153_o;
  wire n2155_o;
  wire [1:0] n2156_o;
  wire [1:0] n2158_o;
  wire n2160_o;
  wire n2161_o;
  wire [30:0] n2165_o;
  reg [3:0] n2169_q = 0;
  reg [3:0] n2170_q = 0;
  reg [3:0] n2171_q = 0;
  wire [1:0] n2172_o;
  reg [1:0] n2173_q = 0;
  wire [3:0] n2174_o;
  wire [1:0] n2176_o;
  wire [3:0] n2177_o;
  wire [3:0] n2178_o;
  assign addr = ph3;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:21:16  */
  assign ph1 = n2169_q; // (signal)
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:21:20  */
  assign ph2 = n2170_q; // (signal)
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:21:24  */
  assign ph3 = n2171_q; // (signal)
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:33:16  */
  always @*
    state = n2173_q; // (isignal)
  initial
    state = 2'b00;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:33:22  */
  always @*
    statenext = n2156_o; // (isignal)
  initial
    statenext = 2'b00;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:35:21  */
  assign n2143_o = phase + 4'b0010;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:35:34  */
  assign n2145_o = n2143_o + 4'b0011;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:39:27  */
  assign n2151_o = state + 2'b10;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:39:30  */
  assign n2153_o = n2151_o - 2'b00;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:39:52  */
  assign n2155_o = $unsigned(state) >= $unsigned(2'b10);
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:39:42  */
  assign n2156_o = n2155_o ? n2153_o : n2158_o;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:39:80  */
  assign n2158_o = state + 2'b10;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:40:36  */
  assign n2160_o = ph1 == 4'b0000;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:40:39  */
  assign n2161_o = n2160_o & reorderenable;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:51:41  */
  assign n2165_o = {29'b0, state};  //  uext
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:35:41  */
  always @(posedge clk)
    n2169_q <= n2145_o;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:38:20  */
  always @(posedge clk)
    n2170_q <= ph1;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:51:60  */
  always @(posedge clk)
    n2171_q <= n2178_o;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:40:28  */
  assign n2172_o = n2161_o ? statenext : state;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:40:28  */
  always @(posedge clk)
    n2173_q <= n2172_o;
  initial
    n2173_q = 2'b00;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:51:24  */
  assign n2174_o = ph2 << n2165_o;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:51:24  */
  assign n2176_o = 2'b00 - state;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:51:24  */
  assign n2177_o = ph2 >> n2176_o;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:51:24  */
  assign n2178_o = n2174_o | n2177_o;
endmodule

module fft4_serial8_bf_10_0
  (input  clk,
   input  [47:0] dina_re,
   input  [47:0] dina_im,
   input  [47:0] dinb_re,
   input  [47:0] dinb_im,
   input  subtractre,
   input  subtractim,
   input  roundrandre,
   input  roundrandim,
   output [47:0] dout_re,
   output [47:0] dout_im);
  wire [95:0] n2082_o;
  wire [95:0] n2083_o;
  wire [47:0] n2085_o;
  wire [47:0] n2086_o;
  wire [95:0] tmp;
  wire [47:0] n2097_o;
  wire [47:0] n2098_o;
  wire [47:0] n2099_o;
  wire n2100_o;
  wire [47:0] n2101_o;
  wire [47:0] n2102_o;
  wire [47:0] n2103_o;
  wire [47:0] n2104_o;
  wire [47:0] n2105_o;
  wire [47:0] n2106_o;
  wire [47:0] n2107_o;
  wire n2108_o;
  wire [47:0] n2109_o;
  wire [47:0] n2110_o;
  wire [47:0] n2111_o;
  wire [47:0] n2112_o;
  wire [47:0] n2121_o;
  wire [47:0] n2123_o;
  wire [9:0] n2125_o;
  wire [47:0] n2126_o;
  wire [9:0] n2129_o;
  wire [47:0] n2130_o;
  wire [95:0] n2131_o;
  wire [95:0] n2135_o;
  reg [95:0] n2138_q = 0;
  assign dout_re = n2085_o;
  assign dout_im = n2086_o;
  assign n2082_o = {dina_im, dina_re};
  assign n2083_o = {dinb_im, dinb_re};
  assign n2085_o = n2138_q[47:0];
  assign n2086_o = n2138_q[95:48];
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:21:16  */
  assign tmp = n2135_o; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:31:32  */
  assign n2097_o = n2082_o[47:0];
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:31:42  */
  assign n2098_o = n2083_o[47:0];
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:31:35  */
  assign n2099_o = n2097_o + n2098_o;
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:31:60  */
  assign n2100_o = ~subtractre;
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:31:45  */
  assign n2101_o = n2100_o ? n2099_o : n2104_o;
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:31:75  */
  assign n2102_o = n2082_o[47:0];
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:31:85  */
  assign n2103_o = n2083_o[47:0];
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:31:78  */
  assign n2104_o = n2102_o - n2103_o;
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:32:32  */
  assign n2105_o = n2082_o[95:48];
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:32:42  */
  assign n2106_o = n2083_o[95:48];
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:32:35  */
  assign n2107_o = n2105_o + n2106_o;
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:32:60  */
  assign n2108_o = ~subtractim;
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:32:45  */
  assign n2109_o = n2108_o ? n2107_o : n2112_o;
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:32:75  */
  assign n2110_o = n2082_o[95:48];
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:32:85  */
  assign n2111_o = n2083_o[95:48];
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:32:78  */
  assign n2112_o = n2110_o - n2111_o;
  /* ../fpga-fft/rtl/fft_types.vhd:192:28  */
  assign n2121_o = tmp[47:0];
  /* ../fpga-fft/rtl/fft_types.vhd:193:28  */
  assign n2123_o = tmp[95:48];
  /* ../fpga-fft/rtl/fft_types.vhd:194:37  */
  assign n2125_o = n2121_o[9:0];
  /* ../fpga-fft/rtl/fft_types.vhd:194:27  */
  assign n2126_o = {{38{n2125_o[9]}}, n2125_o}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:195:37  */
  assign n2129_o = n2123_o[9:0];
  /* ../fpga-fft/rtl/fft_types.vhd:195:27  */
  assign n2130_o = {{38{n2129_o[9]}}, n2129_o}; // sext
  assign n2131_o = {n2130_o, n2126_o};
  assign n2135_o = {n2109_o, n2101_o};
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:56:42  */
  always @(posedge clk)
    n2138_q <= n2131_o;
endmodule

module fft4_serial8_bf_9_0
  (input  clk,
   input  [47:0] dina_re,
   input  [47:0] dina_im,
   input  [47:0] dinb_re,
   input  [47:0] dinb_im,
   input  subtractre,
   input  subtractim,
   input  roundrandre,
   input  roundrandim,
   output [47:0] dout_re,
   output [47:0] dout_im);
  wire [95:0] n2025_o;
  wire [95:0] n2026_o;
  wire [47:0] n2028_o;
  wire [47:0] n2029_o;
  wire [95:0] tmp;
  wire [47:0] n2040_o;
  wire [47:0] n2041_o;
  wire [47:0] n2042_o;
  wire n2043_o;
  wire [47:0] n2044_o;
  wire [47:0] n2045_o;
  wire [47:0] n2046_o;
  wire [47:0] n2047_o;
  wire [47:0] n2048_o;
  wire [47:0] n2049_o;
  wire [47:0] n2050_o;
  wire n2051_o;
  wire [47:0] n2052_o;
  wire [47:0] n2053_o;
  wire [47:0] n2054_o;
  wire [47:0] n2055_o;
  wire [47:0] n2064_o;
  wire [47:0] n2066_o;
  wire [8:0] n2068_o;
  wire [47:0] n2069_o;
  wire [8:0] n2072_o;
  wire [47:0] n2073_o;
  wire [95:0] n2074_o;
  wire [95:0] n2078_o;
  reg [95:0] n2081_q = 0;
  assign dout_re = n2028_o;
  assign dout_im = n2029_o;
  assign n2025_o = {dina_im, dina_re};
  assign n2026_o = {dinb_im, dinb_re};
  /* ../fpga-fft/rtl/fft_types.vhd:137:26  */
  assign n2028_o = n2081_q[47:0];
  assign n2029_o = n2081_q[95:48];
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:21:16  */
  assign tmp = n2078_o; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:31:32  */
  assign n2040_o = n2025_o[47:0];
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:31:42  */
  assign n2041_o = n2026_o[47:0];
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:31:35  */
  assign n2042_o = n2040_o + n2041_o;
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:31:60  */
  assign n2043_o = ~subtractre;
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:31:45  */
  assign n2044_o = n2043_o ? n2042_o : n2047_o;
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:31:75  */
  assign n2045_o = n2025_o[47:0];
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:31:85  */
  assign n2046_o = n2026_o[47:0];
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:31:78  */
  assign n2047_o = n2045_o - n2046_o;
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:32:32  */
  assign n2048_o = n2025_o[95:48];
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:32:42  */
  assign n2049_o = n2026_o[95:48];
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:32:35  */
  assign n2050_o = n2048_o + n2049_o;
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:32:60  */
  assign n2051_o = ~subtractim;
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:32:45  */
  assign n2052_o = n2051_o ? n2050_o : n2055_o;
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:32:75  */
  assign n2053_o = n2025_o[95:48];
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:32:85  */
  assign n2054_o = n2026_o[95:48];
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:32:78  */
  assign n2055_o = n2053_o - n2054_o;
  /* ../fpga-fft/rtl/fft_types.vhd:192:28  */
  assign n2064_o = tmp[47:0];
  /* ../fpga-fft/rtl/fft_types.vhd:193:28  */
  assign n2066_o = tmp[95:48];
  /* ../fpga-fft/rtl/fft_types.vhd:194:37  */
  assign n2068_o = n2064_o[8:0];
  /* ../fpga-fft/rtl/fft_types.vhd:194:27  */
  assign n2069_o = {{39{n2068_o[8]}}, n2068_o}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:195:37  */
  assign n2072_o = n2066_o[8:0];
  /* ../fpga-fft/rtl/fft_types.vhd:195:27  */
  assign n2073_o = {{39{n2072_o[8]}}, n2072_o}; // sext
  assign n2074_o = {n2073_o, n2069_o};
  assign n2078_o = {n2052_o, n2044_o};
  /* ../fpga-fft/rtl/fft4_serial8_bf.vhd:56:42  */
  always @(posedge clk)
    n2081_q <= n2074_o;
endmodule

module twiddlegenerator16_10_bf8b4530d8d246dd74ac53a13471bba17941dff7
  (input  clk,
   input  [3:0] twaddr,
   output [47:0] twdata_re,
   output [47:0] twdata_im);
  wire [47:0] n1989_o;
  wire [47:0] n1990_o;
  wire [351:0] rominverse;
  wire [3:0] addr1;
  wire [21:0] data0;
  wire [21:0] data1;
  wire [3:0] n1995_o;
  wire [10:0] n2007_o;
  wire [10:0] n2008_o;
  wire [47:0] n2014_o;
  wire [47:0] n2017_o;
  wire [95:0] n2018_o;
  reg [3:0] n2021_q = 0;
  reg [21:0] n2022_q = 0;
  wire [21:0] n2024_data; // mem_rd
  assign twdata_re = n1989_o;
  assign twdata_im = n1990_o;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:21:17  */
  assign n1989_o = n2018_o[47:0];
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:51:42  */
  assign n1990_o = n2018_o[95:48];
  /* ../fpga-fft/generated/fft4096/twiddle_generator_16.vhd:23:21  */
  assign rominverse = 352'b0000000000001000000000000110001000011101100100101101010001011010100011101100100011000100010000000000000000000000111011001111001111000010110101011010010110000110001001100010011100000000000110000000001110011110011000100111110100101101101001011011000100111111001111001100000000000000000000110001001110001100010011010010110001011010101110011110000111011001; // (signal)
  /* ../fpga-fft/generated/fft4096/twiddle_generator_16.vhd:24:16  */
  assign addr1 = n2021_q; // (signal)
  /* ../fpga-fft/generated/fft4096/twiddle_generator_16.vhd:25:16  */
  assign data0 = n2024_data; // (signal)
  /* ../fpga-fft/generated/fft4096/twiddle_generator_16.vhd:25:22  */
  assign data1 = n2022_q; // (signal)
  /* ../fpga-fft/generated/fft4096/twiddle_generator_16.vhd:30:37  */
  assign n1995_o = 4'b1111 - addr1;
  /* ../fpga-fft/rtl/fft_types.vhd:160:45  */
  assign n2007_o = data1[10:0];
  /* ../fpga-fft/rtl/fft_types.vhd:161:67  */
  assign n2008_o = data1[21:11];
  /* ../fpga-fft/rtl/fft_types.vhd:139:27  */
  assign n2014_o = {{37{n2007_o[10]}}, n2007_o}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:140:27  */
  assign n2017_o = {{37{n2008_o[10]}}, n2008_o}; // sext
  assign n2018_o = {n2017_o, n2014_o};
  /* ../fpga-fft/generated/fft4096/twiddle_generator_16.vhd:27:25  */
  always @(posedge clk)
    n2021_q <= twaddr;
  /* ../fpga-fft/generated/fft4096/twiddle_generator_16.vhd:35:24  */
  always @(posedge clk)
    n2022_q <= data0;
  /* ../fpga-fft/generated/fft4096/twiddle_generator_16.vhd:13:25  */
  reg [21:0] n2023[15:0] ; // memor = 0;
  initial begin
    n2023[15] = 22'b0000000000001000000000;
    n2023[14] = 22'b0001100010000111011001;
    n2023[13] = 22'b0010110101000101101010;
    n2023[12] = 22'b0011101100100011000100;
    n2023[11] = 22'b0100000000000000000000;
    n2023[10] = 22'b0011101100111100111100;
    n2023[9] = 22'b0010110101011010010110;
    n2023[8] = 22'b0001100010011000100111;
    n2023[7] = 22'b0000000000011000000000;
    n2023[6] = 22'b1110011110011000100111;
    n2023[5] = 22'b1101001011011010010110;
    n2023[4] = 22'b1100010011111100111100;
    n2023[3] = 22'b1100000000000000000000;
    n2023[2] = 22'b1100010011100011000100;
    n2023[1] = 22'b1101001011000101101010;
    n2023[0] = 22'b1110011110000111011001;
    end
  assign n2024_data = n2023[n1995_o];
  /* ../fpga-fft/generated/fft4096/twiddle_generator_16.vhd:30:37  */
endmodule

module twiddleaddrgen_2_2_2_9159cb8bcee7fcb95582f140960cdae72788d326
  (input  clk,
   input  [3:0] phase,
   input  [1:0] bitpermout,
   output [3:0] twaddr,
   output [1:0] bitpermin);
  reg [3:0] ph0 = 0;
  reg [3:0] ph_twiddle = 0;
  reg [1:0] twmajoraddr = 0;
  reg [3:0] twaddr0 = 0;
  reg [3:0] twaddr0next = 0;
  wire [3:0] n1961_o;
  wire [3:0] n1963_o;
  wire [1:0] n1966_o;
  wire [1:0] n1968_o;
  wire [1:0] n1969_o;
  wire [1:0] n1971_o;
  wire n1973_o;
  wire [3:0] n1974_o;
  wire [2:0] n1976_o;
  wire [3:0] n1977_o;
  wire [3:0] n1978_o;
  wire n1979_o;
  wire [3:0] n1980_o;
  wire [3:0] n1981_o;
  wire [3:0] n1982_o;
  reg [3:0] n1985_q = 0;
  reg [3:0] n1987_q = 0;
  assign twaddr = twaddr0;
  assign bitpermin = n1966_o;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:36:22  */
  always @*
    ph0 = phase; // (isignal)
  initial
    ph0 = 4'b0000;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:38:16  */
  always @*
    ph_twiddle = n1985_q; // (isignal)
  initial
    ph_twiddle = 4'b0000;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:39:16  */
  always @*
    twmajoraddr = n1968_o; // (isignal)
  initial
    twmajoraddr = 2'b00;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:41:16  */
  always @*
    twaddr0 = n1987_q; // (isignal)
  initial
    twaddr0 = 4'b0000;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:41:25  */
  always @*
    twaddr0next = n1974_o; // (isignal)
  initial
    twaddr0next = 4'b0000;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:51:26  */
  assign n1961_o = ph0 + 4'b0010;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:51:39  */
  assign n1963_o = n1961_o + 4'b0010;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:53:32  */
  assign n1966_o = ph_twiddle[3:2];
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:54:35  */
  assign n1968_o = 1'b1 ? bitpermout : n1969_o;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:55:27  */
  assign n1969_o = ph_twiddle[3:2];
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:62:61  */
  assign n1971_o = ph_twiddle[1:0];
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:62:83  */
  assign n1973_o = n1971_o == 2'b00;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:62:46  */
  assign n1974_o = n1973_o ? 4'b0000 : n1980_o;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:63:64  */
  assign n1976_o = {twmajoraddr, 1'b0};
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:63:49  */
  assign n1977_o = {1'b0, n1976_o};  //  uext
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:63:49  */
  assign n1978_o = twaddr0 + n1977_o;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:63:86  */
  assign n1979_o = ph_twiddle[0];
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:62:86  */
  assign n1980_o = n1979_o ? n1978_o : n1982_o;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:64:49  */
  assign n1981_o = {2'b0, twmajoraddr};  //  uext
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:64:49  */
  assign n1982_o = twaddr0 - n1981_o;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:51:42  */
  always @(posedge clk)
    n1985_q <= n1963_o;
  initial
    n1985_q = 4'b0000;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:66:32  */
  always @(posedge clk)
    n1987_q <= twaddr0next;
  initial
    n1987_q = 4'b0000;
endmodule

module transposer_2_2_8
  (input  clk,
   input  [47:0] din_re,
   input  [47:0] din_im,
   input  [3:0] phase,
   input  reorderenable,
   output [47:0] dout_re,
   output [47:0] dout_im);
  wire [95:0] n1933_o;
  wire [47:0] n1935_o;
  wire [47:0] n1936_o;
  wire [95:0] din2;
  wire [95:0] dout0;
  wire [95:0] dout1;
  wire [3:0] iaddr;
  wire [3:0] iaddr2;
  wire [3:0] oaddr;
  wire [3:0] gb_addrgen_addr;
  wire [47:0] gb_g3_ram_rddata_re;
  wire [47:0] gb_g3_ram_rddata_im;
  wire [95:0] n1938_o;
  localparam n1940_o = 1'b1;
  wire [47:0] n1941_o;
  wire [47:0] n1942_o;
  wire [3:0] gb_sr1_dout;
  localparam n1944_o = 1'b1;
  reg [95:0] n1949_q = 0;
  reg [3:0] n1950_q = 0;
  assign dout_re = n1935_o;
  assign dout_im = n1936_o;
  assign n1933_o = {din_im, din_re};
  assign n1935_o = dout1[47:0];
  assign n1936_o = dout1[95:48];
  /* ../fpga-fft/rtl/transposer.vhd:31:16  */
  assign din2 = n1949_q; // (signal)
  /* ../fpga-fft/rtl/transposer.vhd:31:22  */
  assign dout0 = n1938_o; // (signal)
  /* ../fpga-fft/rtl/transposer.vhd:31:29  */
  assign dout1 = dout0; // (signal)
  /* ../fpga-fft/rtl/transposer.vhd:32:16  */
  assign iaddr = gb_sr1_dout; // (signal)
  /* ../fpga-fft/rtl/transposer.vhd:32:23  */
  assign iaddr2 = n1950_q; // (signal)
  /* ../fpga-fft/rtl/transposer.vhd:32:31  */
  assign oaddr = gb_addrgen_addr; // (signal)
  /* ../fpga-fft/rtl/transposer.vhd:47:17  */
  transposer_addrgen_2_2_2 gb_addrgen (
    .clk(clk),
    .reorderenable(reorderenable),
    .phase(phase),
    .addr(gb_addrgen_addr));
  /* ../fpga-fft/rtl/transposer.vhd:52:25  */
  complexramlut_8_4 gb_g3_ram (
    .rdclk(clk),
    .wrclk(clk),
    .rdaddr(oaddr),
    .wren(n1940_o),
    .wraddr(iaddr2),
    .wrdata_re(n1941_o),
    .wrdata_im(n1942_o),
    .rddata_re(gb_g3_ram_rddata_re),
    .rddata_im(gb_g3_ram_rddata_im));
  assign n1938_o = {gb_g3_ram_rddata_im, gb_g3_ram_rddata_re};
  /* ../fpga-fft/rtl/fft_types.vhd:190:26  */
  assign n1941_o = din2[47:0];
  assign n1942_o = din2[95:48];
  /* ../fpga-fft/rtl/transposer.vhd:78:17  */
  sr_unsigned_4_2 gb_sr1 (
    .clk(clk),
    .din(oaddr),
    .ce(n1944_o),
    .dout(gb_sr1_dout));
  /* ../fpga-fft/rtl/transposer.vhd:80:29  */
  always @(posedge clk)
    n1949_q <= n1933_o;
  /* ../fpga-fft/rtl/transposer.vhd:81:33  */
  always @(posedge clk)
    n1950_q <= iaddr;
endmodule

module transposer_addrgen_2_4_2
  (input  clk,
   input  reorderenable,
   input  [5:0] phase,
   output [5:0] addr);
  wire [5:0] ph1;
  wire [5:0] ph2;
  wire [5:0] ph3;
  reg [2:0] state = 0;
  reg [2:0] statenext = 0;
  wire [5:0] n1897_o;
  wire [5:0] n1899_o;
  wire [2:0] n1905_o;
  wire [2:0] n1907_o;
  wire n1909_o;
  wire [2:0] n1910_o;
  wire [2:0] n1912_o;
  wire n1914_o;
  wire n1915_o;
  wire [30:0] n1919_o;
  reg [5:0] n1923_q = 0;
  reg [5:0] n1924_q = 0;
  reg [5:0] n1925_q = 0;
  wire [2:0] n1926_o;
  reg [2:0] n1927_q = 0;
  wire [5:0] n1928_o;
  wire [2:0] n1930_o;
  wire [5:0] n1931_o;
  wire [5:0] n1932_o;
  assign addr = ph3;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:21:16  */
  assign ph1 = n1923_q; // (signal)
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:21:20  */
  assign ph2 = n1924_q; // (signal)
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:21:24  */
  assign ph3 = n1925_q; // (signal)
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:33:16  */
  always @*
    state = n1927_q; // (isignal)
  initial
    state = 3'b000;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:33:22  */
  always @*
    statenext = n1910_o; // (isignal)
  initial
    statenext = 3'b000;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:35:21  */
  assign n1897_o = phase + 6'b000010;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:35:34  */
  assign n1899_o = n1897_o + 6'b000011;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:39:27  */
  assign n1905_o = state + 3'b100;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:39:30  */
  assign n1907_o = n1905_o - 3'b110;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:39:52  */
  assign n1909_o = $unsigned(state) >= $unsigned(3'b010);
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:39:42  */
  assign n1910_o = n1909_o ? n1907_o : n1912_o;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:39:80  */
  assign n1912_o = state + 3'b100;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:40:36  */
  assign n1914_o = ph1 == 6'b000000;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:40:39  */
  assign n1915_o = n1914_o & reorderenable;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:51:41  */
  assign n1919_o = {28'b0, state};  //  uext
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:35:41  */
  always @(posedge clk)
    n1923_q <= n1899_o;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:38:20  */
  always @(posedge clk)
    n1924_q <= ph1;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:51:60  */
  always @(posedge clk)
    n1925_q <= n1932_o;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:40:28  */
  assign n1926_o = n1915_o ? statenext : state;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:40:28  */
  always @(posedge clk)
    n1927_q <= n1926_o;
  initial
    n1927_q = 3'b000;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:51:24  */
  assign n1928_o = ph2 << n1919_o;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:51:24  */
  assign n1930_o = 3'b110 - state;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:51:24  */
  assign n1931_o = ph2 >> n1930_o;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:51:24  */
  assign n1932_o = n1928_o | n1931_o;
endmodule

module fft4_serial8_8_0_0_0201fbb6ff0978da8799292b5725f3cbccd5acf0
  (input  clk,
   input  [47:0] din_re,
   input  [47:0] din_im,
   input  [1:0] phase,
   output [47:0] dout_re,
   output [47:0] dout_im);
  wire [95:0] n1622_o;
  wire [47:0] n1624_o;
  wire [47:0] n1625_o;
  wire [1:0] ph1;
  wire [1:0] ph2;
  wire [95:0] din1;
  wire [95:0] bfina;
  wire [95:0] bfinb;
  wire [95:0] bfout;
  wire [95:0] tmp1;
  wire [95:0] tmp2;
  wire [95:0] bf2ina;
  wire [95:0] bf2inb;
  wire [95:0] bf2inanext;
  wire [95:0] bf2inbnext;
  wire [95:0] bf2out;
  wire bfsubtractre;
  wire bfsubtractim;
  wire bf2subtractre;
  wire bf2subtractim;
  wire bf2subtracttmp;
  reg dinbias = 0;
  reg bf1bias = 0;
  reg roundrandre = 0;
  reg roundrandim = 0;
  reg [2:0] roundaddre = 0;
  reg [2:0] roundaddim = 0;
  reg [6:0] lfsr = 0;
  reg [6:0] lfsrnext = 0;
  wire [1:0] ph1_dup0;
  wire [1:0] ph1_dup1;
  wire [47:0] n1654_o;
  wire [47:0] n1656_o;
  wire [7:0] n1658_o;
  wire [47:0] n1659_o;
  wire [7:0] n1662_o;
  wire [47:0] n1663_o;
  wire [95:0] n1664_o;
  wire n1667_o;
  wire n1668_o;
  wire n1672_o;
  wire n1675_o;
  wire n1676_o;
  wire n1677_o;
  wire n1678_o;
  wire n1679_o;
  wire n1680_o;
  wire n1681_o;
  wire n1682_o;
  wire [1:0] n1683_o;
  wire [4:0] n1684_o;
  wire [6:0] n1685_o;
  wire n1692_o;
  wire n1695_o;
  localparam [6:0] n1696_o = 7'b0000000;
  wire n1698_o;
  wire n1700_o;
  wire n1701_o;
  wire n1703_o;
  wire n1705_o;
  wire n1706_o;
  wire n1708_o;
  wire n1710_o;
  wire n1711_o;
  wire n1713_o;
  wire n1715_o;
  wire n1716_o;
  wire n1718_o;
  wire n1720_o;
  wire n1721_o;
  wire n1722_o;
  wire n1723_o;
  wire n1725_o;
  wire [6:0] n1726_o;
  wire n1729_o;
  wire n1732_o;
  wire n1736_o;
  wire [2:0] n1737_o;
  wire [1:0] n1739_o;
  wire n1740_o;
  wire [2:0] n1741_o;
  wire n1743_o;
  wire [2:0] n1744_o;
  wire [1:0] n1746_o;
  wire n1747_o;
  wire [2:0] n1748_o;
  wire [47:0] n1749_o;
  wire [47:0] n1750_o;
  wire [47:0] n1751_o;
  wire n1752_o;
  wire n1753_o;
  wire n1754_o;
  wire n1755_o;
  wire [47:0] n1756_o;
  wire [47:0] n1757_o;
  wire [47:0] n1758_o;
  wire [47:0] n1759_o;
  wire [47:0] n1760_o;
  wire n1761_o;
  wire n1762_o;
  wire n1763_o;
  wire n1764_o;
  wire [47:0] n1765_o;
  wire [47:0] n1766_o;
  wire n1767_o;
  wire n1770_o;
  wire [47:0] bf1_dout_re;
  wire [47:0] bf1_dout_im;
  wire [47:0] n1773_o;
  wire [47:0] n1774_o;
  wire [47:0] n1775_o;
  wire [47:0] n1776_o;
  wire [95:0] n1777_o;
  wire n1779_o;
  wire n1780_o;
  wire n1784_o;
  wire n1788_o;
  wire n1789_o;
  wire [95:0] n1790_o;
  wire n1791_o;
  wire n1792_o;
  wire [95:0] n1793_o;
  wire [47:0] n1795_o;
  wire [47:0] n1796_o;
  wire [95:0] n1804_o;
  wire n1805_o;
  wire n1806_o;
  wire n1810_o;
  wire n1811_o;
  wire n1815_o;
  wire n1816_o;
  wire n1817_o;
  wire n1822_o;
  wire [47:0] bf2_dout_re;
  wire [47:0] bf2_dout_im;
  wire [47:0] n1825_o;
  wire [47:0] n1826_o;
  wire [47:0] n1827_o;
  wire [47:0] n1828_o;
  wire [95:0] n1829_o;
  wire [47:0] n1838_o;
  wire [47:0] n1840_o;
  wire [47:0] n1843_o;
  wire [47:0] n1845_o;
  wire [95:0] n1846_o;
  wire [47:0] n1854_o;
  wire [47:0] n1856_o;
  wire [7:0] n1858_o;
  wire [47:0] n1859_o;
  wire [7:0] n1862_o;
  wire [47:0] n1863_o;
  wire [95:0] n1864_o;
  reg [1:0] n1865_q = 0;
  reg [1:0] n1866_q = 0;
  reg [95:0] n1869_q = 0;
  wire [95:0] n1870_o;
  wire [95:0] n1871_o;
  reg [95:0] n1872_q = 0;
  wire [95:0] n1873_o;
  reg [95:0] n1874_q = 0;
  wire [95:0] n1875_o;
  reg [95:0] n1876_q = 0;
  wire [95:0] n1877_o;
  reg [95:0] n1878_q = 0;
  wire [95:0] n1879_o;
  reg [95:0] n1880_q = 0;
  reg n1881_q = 0;
  reg n1882_q = 0;
  reg n1883_q = 0;
  reg n1884_q = 0;
  reg n1885_q = 0;
  reg n1886_q = 0;
  reg n1887_q = 0;
  reg n1888_q = 0;
  reg [6:0] n1890_q = 0;
  reg [1:0] n1891_q = 0;
  reg [1:0] n1892_q = 0;
  assign dout_re = n1624_o;
  assign dout_im = n1625_o;
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:97:74  */
  assign n1622_o = {din_im, din_re};
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:85:71  */
  assign n1624_o = n1864_o[47:0];
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:78:36  */
  assign n1625_o = n1864_o[95:48];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:43:16  */
  assign ph1 = n1865_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:43:21  */
  assign ph2 = n1866_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:44:16  */
  assign din1 = n1869_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:44:22  */
  assign bfina = n1870_o; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:44:29  */
  assign bfinb = n1872_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:44:36  */
  assign bfout = n1777_o; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:44:43  */
  assign tmp1 = n1874_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:44:49  */
  assign tmp2 = n1876_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:45:16  */
  assign bf2ina = n1878_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:45:24  */
  assign bf2inb = n1880_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:45:32  */
  assign bf2inanext = n1790_o; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:45:44  */
  assign bf2inbnext = n1793_o; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:45:56  */
  assign bf2out = n1829_o; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:46:16  */
  assign bfsubtractre = n1881_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:46:30  */
  assign bfsubtractim = n1882_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:46:44  */
  assign bf2subtractre = n1883_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:46:59  */
  assign bf2subtractim = n1884_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:47:16  */
  assign bf2subtracttmp = n1885_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:49:16  */
  always @*
    dinbias = n1886_q; // (isignal)
  initial
    dinbias = 1'b0;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:50:16  */
  always @*
    bf1bias = 1'b0; // (isignal)
  initial
    bf1bias = 1'b0;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:51:16  */
  always @*
    roundrandre = n1887_q; // (isignal)
  initial
    roundrandre = 1'b0;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:51:29  */
  always @*
    roundrandim = n1888_q; // (isignal)
  initial
    roundrandim = 1'b0;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:52:16  */
  always @*
    roundaddre = n1737_o; // (isignal)
  initial
    roundaddre = 3'b000;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:52:28  */
  always @*
    roundaddim = n1744_o; // (isignal)
  initial
    roundaddim = 3'b000;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:55:16  */
  always @*
    lfsr = n1890_q; // (isignal)
  initial
    lfsr = 7'b1101010;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:55:22  */
  always @*
    lfsrnext = n1685_o; // (isignal)
  initial
    lfsrnext = 7'b1101010;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:59:16  */
  assign ph1_dup0 = n1891_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:59:26  */
  assign ph1_dup1 = n1892_q; // (signal)
  /* ../fpga-fft/rtl/fft_types.vhd:192:28  */
  assign n1654_o = n1622_o[47:0];
  /* ../fpga-fft/rtl/fft_types.vhd:193:28  */
  assign n1656_o = n1622_o[95:48];
  /* ../fpga-fft/rtl/fft_types.vhd:194:37  */
  assign n1658_o = n1654_o[7:0];
  /* ../fpga-fft/rtl/fft_types.vhd:194:27  */
  assign n1659_o = {{40{n1658_o[7]}}, n1658_o}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:195:37  */
  assign n1662_o = n1656_o[7:0];
  /* ../fpga-fft/rtl/fft_types.vhd:195:27  */
  assign n1663_o = {{40{n1662_o[7]}}, n1662_o}; // sext
  assign n1664_o = {n1663_o, n1659_o};
  /* ../fpga-fft/rtl/fft4_serial8.vhd:109:30  */
  assign n1667_o = ph1[0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:109:33  */
  assign n1668_o = ~n1667_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:113:31  */
  assign n1672_o = ph2[1];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:114:33  */
  assign n1675_o = lfsr[0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:114:44  */
  assign n1676_o = lfsr[6];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:114:56  */
  assign n1677_o = lfsr[0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:114:48  */
  assign n1678_o = n1676_o ^ n1677_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:114:71  */
  assign n1679_o = din1[0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:114:60  */
  assign n1680_o = n1678_o ^ n1679_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:114:86  */
  assign n1681_o = din1[49];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:114:75  */
  assign n1682_o = n1680_o ^ n1681_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:114:37  */
  assign n1683_o = {n1675_o, n1682_o};
  /* ../fpga-fft/rtl/fft4_serial8.vhd:114:97  */
  assign n1684_o = lfsr[5:1];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:114:91  */
  assign n1685_o = {n1683_o, n1684_o};
  /* ../fpga-fft/rtl/fft4_serial8.vhd:88:31  */
  assign n1692_o = lfsrnext[6];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:88:25  */
  assign n1695_o = n1692_o ? 1'b1 : 1'b0;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:88:31  */
  assign n1698_o = lfsrnext[5];
  assign n1700_o = n1696_o[5];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:88:25  */
  assign n1701_o = n1698_o ? 1'b1 : n1700_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:88:31  */
  assign n1703_o = lfsrnext[4];
  assign n1705_o = n1696_o[4];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:88:25  */
  assign n1706_o = n1703_o ? 1'b1 : n1705_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:88:31  */
  assign n1708_o = lfsrnext[3];
  assign n1710_o = n1696_o[3];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:88:25  */
  assign n1711_o = n1708_o ? 1'b1 : n1710_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:88:31  */
  assign n1713_o = lfsrnext[2];
  assign n1715_o = n1696_o[2];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:88:25  */
  assign n1716_o = n1713_o ? 1'b1 : n1715_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:88:31  */
  assign n1718_o = lfsrnext[1];
  assign n1720_o = n1696_o[1];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:88:25  */
  assign n1721_o = n1718_o ? 1'b1 : n1720_o;
  assign n1722_o = n1696_o[0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:88:31  */
  assign n1723_o = lfsrnext[0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:88:25  */
  assign n1725_o = n1723_o ? 1'b1 : n1722_o;
  assign n1726_o = {n1695_o, n1701_o, n1706_o, n1711_o, n1716_o, n1721_o, n1725_o};
  /* ../fpga-fft/rtl/fft4_serial8.vhd:117:36  */
  assign n1729_o = lfsr[0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:118:36  */
  assign n1732_o = lfsr[1];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:125:57  */
  assign n1736_o = ~dinbias;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:125:45  */
  assign n1737_o = n1736_o ? 3'b000 : n1741_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:126:61  */
  assign n1739_o = {1'b0, roundrandre};
  /* ../fpga-fft/rtl/fft4_serial8.vhd:126:78  */
  assign n1740_o = ~roundrandre;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:126:75  */
  assign n1741_o = {n1739_o, n1740_o};
  /* ../fpga-fft/rtl/fft4_serial8.vhd:127:57  */
  assign n1743_o = ~dinbias;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:127:45  */
  assign n1744_o = n1743_o ? 3'b000 : n1748_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:128:61  */
  assign n1746_o = {1'b0, roundrandim};
  /* ../fpga-fft/rtl/fft4_serial8.vhd:128:78  */
  assign n1747_o = ~roundrandim;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:128:75  */
  assign n1748_o = {n1746_o, n1747_o};
  /* ../fpga-fft/rtl/fft4_serial8.vhd:130:34  */
  assign n1749_o = din1[47:0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:130:37  */
  assign n1750_o = {{45{roundaddre[2]}}, roundaddre}; // sext
  /* ../fpga-fft/rtl/fft4_serial8.vhd:130:37  */
  assign n1751_o = n1749_o + n1750_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:130:58  */
  assign n1752_o = ph1[0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:130:61  */
  assign n1753_o = ~n1752_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:130:70  */
  assign n1754_o = 1'b0; // posedge
  /* ../fpga-fft/rtl/fft4_serial8.vhd:130:66  */
  assign n1755_o = n1753_o & n1754_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:130:50  */
  assign n1756_o = n1755_o ? n1751_o : n1757_o;
  assign n1757_o = bfina[47:0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:131:34  */
  assign n1758_o = din1[95:48];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:131:37  */
  assign n1759_o = {{45{roundaddim[2]}}, roundaddim}; // sext
  /* ../fpga-fft/rtl/fft4_serial8.vhd:131:37  */
  assign n1760_o = n1758_o + n1759_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:131:58  */
  assign n1761_o = ph1[0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:131:61  */
  assign n1762_o = ~n1761_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:131:70  */
  assign n1763_o = 1'b0; // posedge
  /* ../fpga-fft/rtl/fft4_serial8.vhd:131:66  */
  assign n1764_o = n1762_o & n1763_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:131:50  */
  assign n1765_o = n1764_o ? n1760_o : n1766_o;
  assign n1766_o = bfina[95:48];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:138:28  */
  assign n1767_o = ph1[0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:139:28  */
  assign n1770_o = ph1[0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:141:9  */
  fft4_serial8_bf_9_0 bf1 (
    .clk(clk),
    .dina_re(n1773_o),
    .dina_im(n1774_o),
    .dinb_re(n1775_o),
    .dinb_im(n1776_o),
    .subtractre(bfsubtractre),
    .subtractim(bfsubtractim),
    .roundrandre(bf1bias),
    .roundrandim(bf1bias),
    .dout_re(bf1_dout_re),
    .dout_im(bf1_dout_im));
  assign n1773_o = bfina[47:0];
  assign n1774_o = bfina[95:48];
  assign n1775_o = bfinb[47:0];
  assign n1776_o = bfinb[95:48];
  assign n1777_o = {bf1_dout_im, bf1_dout_re};
  /* ../fpga-fft/rtl/fft4_serial8.vhd:153:31  */
  assign n1779_o = ph2[1];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:153:34  */
  assign n1780_o = ~n1779_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:154:31  */
  assign n1784_o = ph1[1];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:156:41  */
  assign n1788_o = ph1_dup0[1];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:156:44  */
  assign n1789_o = ~n1788_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:156:28  */
  assign n1790_o = n1789_o ? tmp1 : tmp2;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:157:42  */
  assign n1791_o = ph1_dup1[1];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:157:45  */
  assign n1792_o = ~n1791_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:157:29  */
  assign n1793_o = n1792_o ? bfout : n1804_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:157:71  */
  assign n1795_o = tmp1[95:48];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:157:80  */
  assign n1796_o = tmp1[47:0];
  assign n1804_o = {n1796_o, n1795_o};
  /* ../fpga-fft/rtl/fft4_serial8.vhd:158:43  */
  assign n1805_o = ph1_dup0[0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:158:46  */
  assign n1806_o = ~n1805_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:159:43  */
  assign n1810_o = ph1_dup1[0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:159:46  */
  assign n1811_o = ~n1810_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:162:32  */
  assign n1815_o = phase[1];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:162:45  */
  assign n1816_o = phase[0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:162:36  */
  assign n1817_o = n1815_o ^ n1816_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:165:37  */
  assign n1822_o = ph1[0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:172:9  */
  fft4_serial8_bf_10_0 bf2 (
    .clk(clk),
    .dina_re(n1825_o),
    .dina_im(n1826_o),
    .dinb_re(n1827_o),
    .dinb_im(n1828_o),
    .subtractre(bf2subtractre),
    .subtractim(bf2subtractim),
    .roundrandre(roundrandre),
    .roundrandim(roundrandim),
    .dout_re(bf2_dout_re),
    .dout_im(bf2_dout_im));
  assign n1825_o = bf2ina[47:0];
  assign n1826_o = bf2ina[95:48];
  assign n1827_o = bf2inb[47:0];
  assign n1828_o = bf2inb[95:48];
  assign n1829_o = {bf2_dout_im, bf2_dout_re};
  /* ../fpga-fft/rtl/fft_types.vhd:210:43  */
  assign n1838_o = bf2out[47:0];
  /* ../fpga-fft/rtl/fft_types.vhd:210:27  */
  assign n1840_o = $signed(n1838_o) >> 31'b0000000000000000000000000000010;
  /* ../fpga-fft/rtl/fft_types.vhd:211:43  */
  assign n1843_o = bf2out[95:48];
  /* ../fpga-fft/rtl/fft_types.vhd:211:27  */
  assign n1845_o = $signed(n1843_o) >> 31'b0000000000000000000000000000010;
  assign n1846_o = {n1845_o, n1840_o};
  /* ../fpga-fft/rtl/fft_types.vhd:192:28  */
  assign n1854_o = n1846_o[47:0];
  /* ../fpga-fft/rtl/fft_types.vhd:193:28  */
  assign n1856_o = n1846_o[95:48];
  /* ../fpga-fft/rtl/fft_types.vhd:194:37  */
  assign n1858_o = n1854_o[7:0];
  /* ../fpga-fft/rtl/fft_types.vhd:194:27  */
  assign n1859_o = {{40{n1858_o[7]}}, n1858_o}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:195:37  */
  assign n1862_o = n1856_o[7:0];
  /* ../fpga-fft/rtl/fft_types.vhd:195:27  */
  assign n1863_o = {{40{n1862_o[7]}}, n1862_o}; // sext
  assign n1864_o = {n1863_o, n1859_o};
  /* ../fpga-fft/rtl/fft4_serial8.vhd:99:22  */
  always @(posedge clk)
    n1865_q <= phase;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:100:20  */
  always @(posedge clk)
    n1866_q <= ph1;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:107:42  */
  always @(posedge clk)
    n1869_q <= n1664_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:107:42  */
  assign n1870_o = {n1765_o, n1756_o};
  /* ../fpga-fft/rtl/fft4_serial8.vhd:109:22  */
  assign n1871_o = n1668_o ? n1622_o : bfinb;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:109:22  */
  always @(posedge clk)
    n1872_q <= n1871_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:153:23  */
  assign n1873_o = n1780_o ? bfout : tmp1;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:153:23  */
  always @(posedge clk)
    n1874_q <= n1873_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:154:23  */
  assign n1875_o = n1784_o ? bfout : tmp2;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:154:23  */
  always @(posedge clk)
    n1876_q <= n1875_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:158:30  */
  assign n1877_o = n1806_o ? bf2inanext : bf2ina;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:158:30  */
  always @(posedge clk)
    n1878_q <= n1877_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:159:30  */
  assign n1879_o = n1811_o ? bf2inbnext : bf2inb;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:159:30  */
  always @(posedge clk)
    n1880_q <= n1879_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:138:32  */
  always @(posedge clk)
    n1881_q <= n1767_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:139:32  */
  always @(posedge clk)
    n1882_q <= n1770_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:164:49  */
  always @(posedge clk)
    n1883_q <= bf2subtracttmp;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:165:41  */
  always @(posedge clk)
    n1884_q <= n1822_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:162:49  */
  always @(posedge clk)
    n1885_q <= n1817_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:113:35  */
  always @(posedge clk)
    n1886_q <= n1672_o;
  initial
    n1886_q = 1'b0;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:117:40  */
  always @(posedge clk)
    n1887_q <= n1729_o;
  initial
    n1887_q = 1'b0;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:118:40  */
  always @(posedge clk)
    n1888_q <= n1732_o;
  initial
    n1888_q = 1'b0;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:115:55  */
  always @(posedge clk)
    n1890_q <= n1726_o;
  initial
    n1890_q = 7'b1101010;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:104:27  */
  always @(posedge clk)
    n1891_q <= phase;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:105:27  */
  always @(posedge clk)
    n1892_q <= phase;
endmodule

module fft4096_sub16_2_8_10_bf8b4530d8d246dd74ac53a13471bba17941dff7
  (input  clk,
   input  [47:0] din_re,
   input  [47:0] din_im,
   input  [3:0] phase,
   output [47:0] dout_re,
   output [47:0] dout_im);
  wire [95:0] n1573_o;
  wire [47:0] n1575_o;
  wire [47:0] n1576_o;
  wire [95:0] sub1din;
  wire [95:0] sub1dout;
  wire [95:0] sub2din;
  wire [95:0] sub2dout;
  wire [1:0] sub1phase;
  wire [1:0] sub2phase;
  wire [3:0] ph1;
  wire [3:0] ph2;
  wire [3:0] ph3;
  wire [95:0] transpout;
  wire [1:0] bitpermin;
  wire [1:0] bitpermout;
  wire [3:0] twaddr;
  wire [95:0] twdata;
  wire [1:0] n1577_o;
  wire [3:0] n1579_o;
  wire [3:0] n1581_o;
  wire [47:0] transp_dout_re;
  wire [47:0] transp_dout_im;
  wire [47:0] n1584_o;
  wire [47:0] n1585_o;
  wire [95:0] n1586_o;
  localparam n1588_o = 1'b1;
  wire [3:0] twag_twaddr;
  wire [1:0] twag_bitpermin;
  wire [47:0] twmult_out1_re;
  wire [47:0] twmult_out1_im;
  wire [47:0] n1591_o;
  wire [47:0] n1592_o;
  wire [47:0] n1593_o;
  wire [47:0] n1594_o;
  wire [95:0] n1595_o;
  wire [3:0] n1598_o;
  wire [3:0] n1600_o;
  wire [1:0] n1603_o;
  wire n1604_o;
  wire n1605_o;
  wire [1:0] n1606_o;
  wire [47:0] tw_twdata_re;
  wire [47:0] tw_twdata_im;
  wire [95:0] n1607_o;
  wire [47:0] sub1inst_dout_re;
  wire [47:0] sub1inst_dout_im;
  wire [47:0] n1609_o;
  wire [47:0] n1610_o;
  wire [95:0] n1611_o;
  wire [47:0] sub2inst_dout_re;
  wire [47:0] sub2inst_dout_im;
  wire [47:0] n1613_o;
  wire [47:0] n1614_o;
  wire [95:0] n1615_o;
  reg [3:0] n1617_q = 0;
  reg [3:0] n1618_q = 0;
  assign dout_re = n1575_o;
  assign dout_im = n1576_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:151:39  */
  assign n1573_o = {din_im, din_re};
  /* ../fpga-fft/rtl/fft4_serial8.vhd:162:49  */
  assign n1575_o = sub2dout[47:0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:102:20  */
  assign n1576_o = sub2dout[95:48];
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:28:16  */
  assign sub1din = n1573_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:28:25  */
  assign sub1dout = n1611_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:28:35  */
  assign sub2din = n1595_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:28:44  */
  assign sub2dout = n1615_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:29:16  */
  assign sub1phase = n1577_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:30:16  */
  assign sub2phase = n1603_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:44:16  */
  assign ph1 = n1617_q; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:44:21  */
  assign ph2 = ph1; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:44:26  */
  assign ph3 = n1618_q; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:45:22  */
  assign transpout = n1586_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:46:16  */
  assign bitpermin = twag_bitpermin; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:46:26  */
  assign bitpermout = n1606_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:49:16  */
  assign twaddr = twag_twaddr; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:50:16  */
  assign twdata = n1607_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:57:27  */
  assign n1577_o = phase[1:0];
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:59:21  */
  assign n1579_o = phase - 4'b0111;
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:59:23  */
  assign n1581_o = n1579_o + 4'b0001;
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:61:9  */
  transposer_2_2_8 transp (
    .clk(clk),
    .din_re(n1584_o),
    .din_im(n1585_o),
    .phase(ph1),
    .reorderenable(n1588_o),
    .dout_re(transp_dout_re),
    .dout_im(transp_dout_im));
  assign n1584_o = sub1dout[47:0];
  assign n1585_o = sub1dout[95:48];
  /* ../fpga-fft/rtl/fft_types.vhd:137:26  */
  assign n1586_o = {transp_dout_im, transp_dout_re};
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:67:9  */
  twiddleaddrgen_2_2_2_9159cb8bcee7fcb95582f140960cdae72788d326 twag (
    .clk(clk),
    .phase(ph2),
    .bitpermout(bitpermout),
    .twaddr(twag_twaddr),
    .bitpermin(twag_bitpermin));
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:81:9  */
  complexmultiply2_11_8_8_bf8b4530d8d246dd74ac53a13471bba17941dff7 twmult (
    .clk(clk),
    .in1_re(n1591_o),
    .in1_im(n1592_o),
    .in2_re(n1593_o),
    .in2_im(n1594_o),
    .out1_re(twmult_out1_re),
    .out1_im(twmult_out1_im));
  /* ../fpga-fft/rtl/fft4_serial8.vhd:153:39  */
  assign n1591_o = twdata[47:0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:134:47  */
  assign n1592_o = twdata[95:48];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:109:38  */
  assign n1593_o = transpout[47:0];
  assign n1594_o = transpout[95:48];
  assign n1595_o = {twmult_out1_im, twmult_out1_re};
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:87:19  */
  assign n1598_o = ph2 - 4'b0101;
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:87:21  */
  assign n1600_o = n1598_o + 4'b0001;
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:88:25  */
  assign n1603_o = ph3[1:0];
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:90:32  */
  assign n1604_o = bitpermin[0];
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:90:45  */
  assign n1605_o = bitpermin[1];
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:90:35  */
  assign n1606_o = {n1604_o, n1605_o};
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:92:9  */
  twiddlegenerator16_10_bf8b4530d8d246dd74ac53a13471bba17941dff7 tw (
    .clk(clk),
    .twaddr(twaddr),
    .twdata_re(tw_twdata_re),
    .twdata_im(tw_twdata_im));
  /* ../fpga-fft/rtl/fft4_serial8.vhd:102:25  */
  assign n1607_o = {tw_twdata_im, tw_twdata_re};
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:95:9  */
  fft4_serial8_8_0_0_0201fbb6ff0978da8799292b5725f3cbccd5acf0 sub1inst (
    .clk(clk),
    .din_re(n1609_o),
    .din_im(n1610_o),
    .phase(sub1phase),
    .dout_re(sub1inst_dout_re),
    .dout_im(sub1inst_dout_im));
  assign n1609_o = sub1din[47:0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:55:16  */
  assign n1610_o = sub1din[95:48];
  assign n1611_o = {sub1inst_dout_im, sub1inst_dout_re};
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:98:9  */
  fft4_serial8_8_0_0_0201fbb6ff0978da8799292b5725f3cbccd5acf0 sub2inst (
    .clk(clk),
    .din_re(n1613_o),
    .din_im(n1614_o),
    .phase(sub2phase),
    .dout_re(sub2inst_dout_re),
    .dout_im(sub2inst_dout_im));
  assign n1613_o = sub2din[47:0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:52:16  */
  assign n1614_o = sub2din[95:48];
  assign n1615_o = {sub2inst_dout_im, sub2inst_dout_re};
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:59:26  */
  always @(posedge clk)
    n1617_q <= n1581_o;
  /* ../fpga-fft/generated/fft4096/fft4096_sub16_2.vhd:87:24  */
  always @(posedge clk)
    n1618_q <= n1600_o;
endmodule

module fft4_serial8_8_0_2_0201fbb6ff0978da8799292b5725f3cbccd5acf0
  (input  clk,
   input  [47:0] din_re,
   input  [47:0] din_im,
   input  [1:0] phase,
   output [47:0] dout_re,
   output [47:0] dout_im);
  wire [95:0] n1395_o;
  wire [47:0] n1397_o;
  wire [47:0] n1398_o;
  wire [1:0] ph1;
  wire [1:0] ph2;
  wire [95:0] din1;
  wire [95:0] bfina;
  wire [95:0] bfinb;
  wire [95:0] bfout;
  wire [95:0] tmp1;
  wire [95:0] tmp2;
  wire [95:0] bf2ina;
  wire [95:0] bf2inb;
  wire [95:0] bf2inanext;
  wire [95:0] bf2inbnext;
  wire [95:0] bf2out;
  wire bfsubtractre;
  wire bfsubtractim;
  wire bf2subtractre;
  wire bf2subtractim;
  wire bf2subtracttmp;
  reg bf1bias = 0;
  reg roundrandre = 0;
  reg roundrandim = 0;
  wire [1:0] ph1_dup0;
  wire [1:0] ph1_dup1;
  wire [47:0] n1427_o;
  wire [47:0] n1429_o;
  wire [7:0] n1431_o;
  wire [47:0] n1432_o;
  wire [7:0] n1435_o;
  wire [47:0] n1436_o;
  wire [95:0] n1437_o;
  wire n1440_o;
  wire n1441_o;
  wire n1445_o;
  wire n1446_o;
  wire n1450_o;
  wire n1453_o;
  wire [47:0] bf1_dout_re;
  wire [47:0] bf1_dout_im;
  wire [47:0] n1456_o;
  wire [47:0] n1457_o;
  wire [47:0] n1458_o;
  wire [47:0] n1459_o;
  wire [95:0] n1460_o;
  wire n1462_o;
  wire n1463_o;
  wire n1467_o;
  wire n1471_o;
  wire n1472_o;
  wire [95:0] n1473_o;
  wire n1474_o;
  wire n1475_o;
  wire [95:0] n1476_o;
  wire [47:0] n1478_o;
  wire [47:0] n1479_o;
  wire [95:0] n1487_o;
  wire n1488_o;
  wire n1489_o;
  wire n1493_o;
  wire n1494_o;
  wire n1498_o;
  wire n1499_o;
  wire n1500_o;
  wire n1505_o;
  wire [47:0] bf2_dout_re;
  wire [47:0] bf2_dout_im;
  wire [47:0] n1508_o;
  wire [47:0] n1509_o;
  wire [47:0] n1510_o;
  wire [47:0] n1511_o;
  wire [95:0] n1512_o;
  wire [47:0] n1521_o;
  wire [47:0] n1523_o;
  wire [47:0] n1526_o;
  wire [47:0] n1528_o;
  wire [95:0] n1529_o;
  wire [47:0] n1537_o;
  wire [47:0] n1539_o;
  wire [7:0] n1541_o;
  wire [47:0] n1542_o;
  wire [7:0] n1545_o;
  wire [47:0] n1546_o;
  wire [95:0] n1547_o;
  reg [1:0] n1548_q = 0;
  reg [1:0] n1549_q = 0;
  reg [95:0] n1552_q = 0;
  wire [95:0] n1553_o;
  reg [95:0] n1554_q = 0;
  wire [95:0] n1555_o;
  reg [95:0] n1556_q = 0;
  wire [95:0] n1557_o;
  reg [95:0] n1558_q = 0;
  wire [95:0] n1559_o;
  reg [95:0] n1560_q = 0;
  wire [95:0] n1561_o;
  reg [95:0] n1562_q = 0;
  wire [95:0] n1563_o;
  reg [95:0] n1564_q = 0;
  reg n1565_q = 0;
  reg n1566_q = 0;
  reg n1567_q = 0;
  reg n1568_q = 0;
  reg n1569_q = 0;
  reg [1:0] n1571_q = 0;
  reg [1:0] n1572_q = 0;
  assign dout_re = n1397_o;
  assign dout_im = n1398_o;
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:97:74  */
  assign n1395_o = {din_im, din_re};
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:85:71  */
  assign n1397_o = n1547_o[47:0];
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:78:36  */
  assign n1398_o = n1547_o[95:48];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:43:16  */
  assign ph1 = n1548_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:43:21  */
  assign ph2 = n1549_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:44:16  */
  assign din1 = n1552_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:44:22  */
  assign bfina = n1554_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:44:29  */
  assign bfinb = n1556_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:44:36  */
  assign bfout = n1460_o; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:44:43  */
  assign tmp1 = n1558_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:44:49  */
  assign tmp2 = n1560_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:45:16  */
  assign bf2ina = n1562_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:45:24  */
  assign bf2inb = n1564_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:45:32  */
  assign bf2inanext = n1473_o; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:45:44  */
  assign bf2inbnext = n1476_o; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:45:56  */
  assign bf2out = n1512_o; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:46:16  */
  assign bfsubtractre = n1565_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:46:30  */
  assign bfsubtractim = n1566_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:46:44  */
  assign bf2subtractre = n1567_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:46:59  */
  assign bf2subtractim = n1568_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:47:16  */
  assign bf2subtracttmp = n1569_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:50:16  */
  always @*
    bf1bias = 1'b0; // (isignal)
  initial
    bf1bias = 1'b0;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:51:16  */
  always @*
    roundrandre = 1'b0; // (isignal)
  initial
    roundrandre = 1'b0;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:51:29  */
  always @*
    roundrandim = 1'b0; // (isignal)
  initial
    roundrandim = 1'b0;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:59:16  */
  assign ph1_dup0 = n1571_q; // (signal)
  /* ../fpga-fft/rtl/fft4_serial8.vhd:59:26  */
  assign ph1_dup1 = n1572_q; // (signal)
  /* ../fpga-fft/rtl/fft_types.vhd:192:28  */
  assign n1427_o = n1395_o[47:0];
  /* ../fpga-fft/rtl/fft_types.vhd:193:28  */
  assign n1429_o = n1395_o[95:48];
  /* ../fpga-fft/rtl/fft_types.vhd:194:37  */
  assign n1431_o = n1427_o[7:0];
  /* ../fpga-fft/rtl/fft_types.vhd:194:27  */
  assign n1432_o = {{40{n1431_o[7]}}, n1431_o}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:195:37  */
  assign n1435_o = n1429_o[7:0];
  /* ../fpga-fft/rtl/fft_types.vhd:195:27  */
  assign n1436_o = {{40{n1435_o[7]}}, n1435_o}; // sext
  assign n1437_o = {n1436_o, n1432_o};
  /* ../fpga-fft/rtl/fft4_serial8.vhd:109:30  */
  assign n1440_o = ph1[0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:109:33  */
  assign n1441_o = ~n1440_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:134:39  */
  assign n1445_o = ph1[0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:134:42  */
  assign n1446_o = ~n1445_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:138:28  */
  assign n1450_o = ph1[0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:139:28  */
  assign n1453_o = ph1[0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:141:9  */
  fft4_serial8_bf_9_0 bf1 (
    .clk(clk),
    .dina_re(n1456_o),
    .dina_im(n1457_o),
    .dinb_re(n1458_o),
    .dinb_im(n1459_o),
    .subtractre(bfsubtractre),
    .subtractim(bfsubtractim),
    .roundrandre(bf1bias),
    .roundrandim(bf1bias),
    .dout_re(bf1_dout_re),
    .dout_im(bf1_dout_im));
  assign n1456_o = bfina[47:0];
  assign n1457_o = bfina[95:48];
  assign n1458_o = bfinb[47:0];
  assign n1459_o = bfinb[95:48];
  assign n1460_o = {bf1_dout_im, bf1_dout_re};
  /* ../fpga-fft/rtl/fft4_serial8.vhd:153:31  */
  assign n1462_o = ph2[1];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:153:34  */
  assign n1463_o = ~n1462_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:154:31  */
  assign n1467_o = ph1[1];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:156:41  */
  assign n1471_o = ph1_dup0[1];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:156:44  */
  assign n1472_o = ~n1471_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:156:28  */
  assign n1473_o = n1472_o ? tmp1 : tmp2;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:157:42  */
  assign n1474_o = ph1_dup1[1];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:157:45  */
  assign n1475_o = ~n1474_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:157:29  */
  assign n1476_o = n1475_o ? bfout : n1487_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:157:71  */
  assign n1478_o = tmp1[95:48];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:157:80  */
  assign n1479_o = tmp1[47:0];
  assign n1487_o = {n1479_o, n1478_o};
  /* ../fpga-fft/rtl/fft4_serial8.vhd:158:43  */
  assign n1488_o = ph1_dup0[0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:158:46  */
  assign n1489_o = ~n1488_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:159:43  */
  assign n1493_o = ph1_dup1[0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:159:46  */
  assign n1494_o = ~n1493_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:162:32  */
  assign n1498_o = phase[1];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:162:45  */
  assign n1499_o = phase[0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:162:36  */
  assign n1500_o = n1498_o ^ n1499_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:165:37  */
  assign n1505_o = ph1[0];
  /* ../fpga-fft/rtl/fft4_serial8.vhd:172:9  */
  fft4_serial8_bf_10_0 bf2 (
    .clk(clk),
    .dina_re(n1508_o),
    .dina_im(n1509_o),
    .dinb_re(n1510_o),
    .dinb_im(n1511_o),
    .subtractre(bf2subtractre),
    .subtractim(bf2subtractim),
    .roundrandre(roundrandre),
    .roundrandim(roundrandim),
    .dout_re(bf2_dout_re),
    .dout_im(bf2_dout_im));
  assign n1508_o = bf2ina[47:0];
  assign n1509_o = bf2ina[95:48];
  assign n1510_o = bf2inb[47:0];
  assign n1511_o = bf2inb[95:48];
  assign n1512_o = {bf2_dout_im, bf2_dout_re};
  /* ../fpga-fft/rtl/fft_types.vhd:210:43  */
  assign n1521_o = bf2out[47:0];
  /* ../fpga-fft/rtl/fft_types.vhd:210:27  */
  assign n1523_o = $signed(n1521_o) >> 31'b0000000000000000000000000000000;
  /* ../fpga-fft/rtl/fft_types.vhd:211:43  */
  assign n1526_o = bf2out[95:48];
  /* ../fpga-fft/rtl/fft_types.vhd:211:27  */
  assign n1528_o = $signed(n1526_o) >> 31'b0000000000000000000000000000000;
  assign n1529_o = {n1528_o, n1523_o};
  /* ../fpga-fft/rtl/fft_types.vhd:192:28  */
  assign n1537_o = n1529_o[47:0];
  /* ../fpga-fft/rtl/fft_types.vhd:193:28  */
  assign n1539_o = n1529_o[95:48];
  /* ../fpga-fft/rtl/fft_types.vhd:194:37  */
  assign n1541_o = n1537_o[7:0];
  /* ../fpga-fft/rtl/fft_types.vhd:194:27  */
  assign n1542_o = {{40{n1541_o[7]}}, n1541_o}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:195:37  */
  assign n1545_o = n1539_o[7:0];
  /* ../fpga-fft/rtl/fft_types.vhd:195:27  */
  assign n1546_o = {{40{n1545_o[7]}}, n1545_o}; // sext
  assign n1547_o = {n1546_o, n1542_o};
  /* ../fpga-fft/rtl/fft4_serial8.vhd:99:22  */
  always @(posedge clk)
    n1548_q <= phase;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:100:20  */
  always @(posedge clk)
    n1549_q <= ph1;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:107:42  */
  always @(posedge clk)
    n1552_q <= n1437_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:134:31  */
  assign n1553_o = n1446_o ? din1 : bfina;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:134:31  */
  always @(posedge clk)
    n1554_q <= n1553_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:109:22  */
  assign n1555_o = n1441_o ? n1395_o : bfinb;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:109:22  */
  always @(posedge clk)
    n1556_q <= n1555_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:153:23  */
  assign n1557_o = n1463_o ? bfout : tmp1;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:153:23  */
  always @(posedge clk)
    n1558_q <= n1557_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:154:23  */
  assign n1559_o = n1467_o ? bfout : tmp2;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:154:23  */
  always @(posedge clk)
    n1560_q <= n1559_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:158:30  */
  assign n1561_o = n1489_o ? bf2inanext : bf2ina;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:158:30  */
  always @(posedge clk)
    n1562_q <= n1561_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:159:30  */
  assign n1563_o = n1494_o ? bf2inbnext : bf2inb;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:159:30  */
  always @(posedge clk)
    n1564_q <= n1563_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:138:32  */
  always @(posedge clk)
    n1565_q <= n1450_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:139:32  */
  always @(posedge clk)
    n1566_q <= n1453_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:164:49  */
  always @(posedge clk)
    n1567_q <= bf2subtracttmp;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:165:41  */
  always @(posedge clk)
    n1568_q <= n1505_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:162:49  */
  always @(posedge clk)
    n1569_q <= n1500_o;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:104:27  */
  always @(posedge clk)
    n1571_q <= phase;
  /* ../fpga-fft/rtl/fft4_serial8.vhd:105:27  */
  always @(posedge clk)
    n1572_q <= phase;
endmodule

module fft4096_sub16_8_10_bf8b4530d8d246dd74ac53a13471bba17941dff7
  (input  clk,
   input  [47:0] din_re,
   input  [47:0] din_im,
   input  [3:0] phase,
   output [47:0] dout_re,
   output [47:0] dout_im);
  wire [95:0] n1346_o;
  wire [47:0] n1348_o;
  wire [47:0] n1349_o;
  wire [95:0] sub1din;
  wire [95:0] sub1dout;
  wire [95:0] sub2din;
  wire [95:0] sub2dout;
  wire [1:0] sub1phase;
  wire [1:0] sub2phase;
  wire [3:0] ph1;
  wire [3:0] ph2;
  wire [3:0] ph3;
  wire [95:0] transpout;
  wire [1:0] bitpermin;
  wire [1:0] bitpermout;
  wire [3:0] twaddr;
  wire [95:0] twdata;
  wire [1:0] n1350_o;
  wire [3:0] n1352_o;
  wire [3:0] n1354_o;
  wire [47:0] transp_dout_re;
  wire [47:0] transp_dout_im;
  wire [47:0] n1357_o;
  wire [47:0] n1358_o;
  wire [95:0] n1359_o;
  localparam n1361_o = 1'b1;
  wire [3:0] twag_twaddr;
  wire [1:0] twag_bitpermin;
  wire [47:0] twmult_out1_re;
  wire [47:0] twmult_out1_im;
  wire [47:0] n1364_o;
  wire [47:0] n1365_o;
  wire [47:0] n1366_o;
  wire [47:0] n1367_o;
  wire [95:0] n1368_o;
  wire [3:0] n1371_o;
  wire [3:0] n1373_o;
  wire [1:0] n1376_o;
  wire n1377_o;
  wire n1378_o;
  wire [1:0] n1379_o;
  wire [47:0] tw_twdata_re;
  wire [47:0] tw_twdata_im;
  wire [95:0] n1380_o;
  wire [47:0] sub1inst_dout_re;
  wire [47:0] sub1inst_dout_im;
  wire [47:0] n1382_o;
  wire [47:0] n1383_o;
  wire [95:0] n1384_o;
  wire [47:0] sub2inst_dout_re;
  wire [47:0] sub2inst_dout_im;
  wire [47:0] n1386_o;
  wire [47:0] n1387_o;
  wire [95:0] n1388_o;
  reg [3:0] n1390_q = 0;
  reg [3:0] n1391_q = 0;
  assign dout_re = n1348_o;
  assign dout_im = n1349_o;
  /* ../fpga-fft/generated/fft4096/twiddle_rom_64.vhd:31:22  */
  assign n1346_o = {din_im, din_re};
  assign n1348_o = sub2dout[47:0];
  /* ../fpga-fft/rtl/fft_types.vhd:49:14  */
  assign n1349_o = sub2dout[95:48];
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:28:16  */
  assign sub1din = n1346_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:28:25  */
  assign sub1dout = n1384_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:28:35  */
  assign sub2din = n1368_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:28:44  */
  assign sub2dout = n1388_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:29:16  */
  assign sub1phase = n1350_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:30:16  */
  assign sub2phase = n1376_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:44:16  */
  assign ph1 = n1390_q; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:44:21  */
  assign ph2 = ph1; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:44:26  */
  assign ph3 = n1391_q; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:45:22  */
  assign transpout = n1359_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:46:16  */
  assign bitpermin = twag_bitpermin; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:46:26  */
  assign bitpermout = n1379_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:49:16  */
  assign twaddr = twag_twaddr; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:50:16  */
  assign twdata = n1380_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:57:27  */
  assign n1350_o = phase[1:0];
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:59:21  */
  assign n1352_o = phase - 4'b0111;
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:59:23  */
  assign n1354_o = n1352_o + 4'b0001;
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:61:9  */
  transposer_2_2_8 transp (
    .clk(clk),
    .din_re(n1357_o),
    .din_im(n1358_o),
    .phase(ph1),
    .reorderenable(n1361_o),
    .dout_re(transp_dout_re),
    .dout_im(transp_dout_im));
  assign n1357_o = sub1dout[47:0];
  /* ../fpga-fft/rtl/fft_types.vhd:129:26  */
  assign n1358_o = sub1dout[95:48];
  assign n1359_o = {transp_dout_im, transp_dout_re};
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:67:9  */
  twiddleaddrgen_2_2_2_9159cb8bcee7fcb95582f140960cdae72788d326 twag (
    .clk(clk),
    .phase(ph2),
    .bitpermout(bitpermout),
    .twaddr(twag_twaddr),
    .bitpermin(twag_bitpermin));
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:81:9  */
  complexmultiply2_11_8_8_bf8b4530d8d246dd74ac53a13471bba17941dff7 twmult (
    .clk(clk),
    .in1_re(n1364_o),
    .in1_im(n1365_o),
    .in2_re(n1366_o),
    .in2_im(n1367_o),
    .out1_re(twmult_out1_re),
    .out1_im(twmult_out1_im));
  /* ../fpga-fft/rtl/fft_types.vhd:129:26  */
  assign n1364_o = twdata[47:0];
  assign n1365_o = twdata[95:48];
  /* ../fpga-fft/rtl/fft_types.vhd:49:14  */
  assign n1366_o = transpout[47:0];
  /* ../fpga-fft/rtl/fft_types.vhd:49:14  */
  assign n1367_o = transpout[95:48];
  assign n1368_o = {twmult_out1_im, twmult_out1_re};
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:87:19  */
  assign n1371_o = ph2 - 4'b0101;
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:87:21  */
  assign n1373_o = n1371_o + 4'b0001;
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:88:25  */
  assign n1376_o = ph3[1:0];
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:90:32  */
  assign n1377_o = bitpermin[0];
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:90:45  */
  assign n1378_o = bitpermin[1];
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:90:35  */
  assign n1379_o = {n1377_o, n1378_o};
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:92:9  */
  twiddlegenerator16_10_bf8b4530d8d246dd74ac53a13471bba17941dff7 tw (
    .clk(clk),
    .twaddr(twaddr),
    .twdata_re(tw_twdata_re),
    .twdata_im(tw_twdata_im));
  assign n1380_o = {tw_twdata_im, tw_twdata_re};
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:95:9  */
  fft4_serial8_8_0_2_0201fbb6ff0978da8799292b5725f3cbccd5acf0 sub1inst (
    .clk(clk),
    .din_re(n1382_o),
    .din_im(n1383_o),
    .phase(sub1phase),
    .dout_re(sub1inst_dout_re),
    .dout_im(sub1inst_dout_im));
  assign n1382_o = sub1din[47:0];
  assign n1383_o = sub1din[95:48];
  assign n1384_o = {sub1inst_dout_im, sub1inst_dout_re};
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:98:9  */
  fft4_serial8_8_0_2_0201fbb6ff0978da8799292b5725f3cbccd5acf0 sub2inst (
    .clk(clk),
    .din_re(n1386_o),
    .din_im(n1387_o),
    .phase(sub2phase),
    .dout_re(sub2inst_dout_re),
    .dout_im(sub2inst_dout_im));
  assign n1386_o = sub2din[47:0];
  assign n1387_o = sub2din[95:48];
  assign n1388_o = {sub2inst_dout_im, sub2inst_dout_re};
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:59:26  */
  always @(posedge clk)
    n1390_q <= n1354_o;
  /* ../fpga-fft/generated/fft4096/fft4096_sub16.vhd:87:24  */
  always @(posedge clk)
    n1391_q <= n1373_o;
endmodule

module twiddlerom64_10
  (input  clk,
   input  [2:0] romaddr,
   output [17:0] romdata);
  wire [143:0] rom;
  wire [2:0] addr1;
  wire [17:0] data0;
  wire [17:0] data1;
  wire [2:0] n1336_o;
  reg [2:0] n1342_q = 0;
  reg [17:0] n1343_q = 0;
  wire [17:0] n1345_data; // mem_rd
  assign romdata = data1;
  /* ../fpga-fft/generated/fft4096/twiddle_rom_64.vhd:22:16  */
  assign rom = 144'b000110010111111110001100100111110110010010101111101010011000100111011001011110001111000100100011100110101010101000101110001100101101010101101010; // (signal)
  /* ../fpga-fft/generated/fft4096/twiddle_rom_64.vhd:23:16  */
  assign addr1 = n1342_q; // (signal)
  /* ../fpga-fft/generated/fft4096/twiddle_rom_64.vhd:24:16  */
  assign data0 = n1345_data; // (signal)
  /* ../fpga-fft/generated/fft4096/twiddle_rom_64.vhd:24:22  */
  assign data1 = n1343_q; // (signal)
  /* ../fpga-fft/generated/fft4096/twiddle_rom_64.vhd:31:22  */
  assign n1336_o = 3'b111 - addr1;
  /* ../fpga-fft/generated/fft4096/twiddle_rom_64.vhd:30:26  */
  always @(posedge clk)
    n1342_q <= romaddr;
  /* ../fpga-fft/generated/fft4096/twiddle_rom_64.vhd:32:24  */
  always @(posedge clk)
    n1343_q <= data0;
  /* ../fpga-fft/generated/fft4096/twiddle_rom_64.vhd:12:25  */
  reg [17:0] n1344[7:0] ; // memor = 0;
  initial begin
    n1344[7] = 18'b000110010111111110;
    n1344[6] = 18'b001100100111110110;
    n1344[5] = 18'b010010101111101010;
    n1344[4] = 18'b011000100111011001;
    n1344[3] = 18'b011110001111000100;
    n1344[2] = 18'b100011100110101010;
    n1344[1] = 18'b101000101110001100;
    n1344[0] = 18'b101101010101101010;
    end
  assign n1345_data = n1344[n1336_o];
  /* ../fpga-fft/generated/fft4096/twiddle_rom_64.vhd:31:22  */
endmodule

module twiddlegenerator_10_6_2_3f29546453678b855931c174a97d6c0894b8f546
  (input  clk,
   input  [5:0] rdaddr,
   input  [17:0] romdata,
   output [47:0] rddata_re,
   output [47:0] rddata_im,
   output [2:0] romaddr);
  wire [47:0] n1140_o;
  wire [47:0] n1141_o;
  wire [17:0] romdata1;
  reg [2:0] romaddr0 = 0;
  reg [2:0] romaddrnext = 0;
  reg [5:0] phase = 0;
  reg [5:0] phase1 = 0;
  reg [5:0] phase2 = 0;
  reg [5:0] phase3 = 0;
  reg [2:0] ph3 = 0;
  reg [2:0] ph4 = 0;
  wire iszero;
  wire iszeronext;
  wire [31:0] re;
  wire [31:0] im;
  wire [31:0] re0;
  wire [31:0] im0;
  wire [31:0] re_p;
  wire [31:0] re_m;
  wire [31:0] im_p;
  wire [31:0] im_m;
  wire [95:0] outdata;
  wire [95:0] outdata0;
  wire [2:0] n1151_o;
  wire [2:0] n1153_o;
  wire n1154_o;
  wire n1155_o;
  wire [2:0] n1156_o;
  wire [2:0] n1157_o;
  wire [2:0] n1158_o;
  wire [5:0] sr_dout;
  localparam n1164_o = 1'b1;
  wire [3:0] n1168_o;
  wire n1170_o;
  wire n1171_o;
  wire [31:0] n1178_o;
  wire [8:0] n1179_o;
  wire [30:0] n1180_o;
  wire [31:0] n1181_o;
  wire [31:0] n1183_o;
  wire [8:0] n1184_o;
  wire [30:0] n1185_o;
  wire [31:0] n1186_o;
  wire [2:0] n1193_o;
  wire [31:0] n1196_o;
  wire [31:0] n1201_o;
  wire [47:0] n1212_o;
  wire [47:0] n1215_o;
  wire [95:0] n1216_o;
  wire n1218_o;
  wire [95:0] n1219_o;
  wire [47:0] n1226_o;
  wire [47:0] n1229_o;
  wire [95:0] n1230_o;
  wire n1232_o;
  wire [95:0] n1233_o;
  wire [47:0] n1240_o;
  wire [47:0] n1243_o;
  wire [95:0] n1244_o;
  wire n1246_o;
  wire [95:0] n1247_o;
  wire [47:0] n1254_o;
  wire [47:0] n1257_o;
  wire [95:0] n1258_o;
  wire n1260_o;
  wire [95:0] n1261_o;
  wire [47:0] n1268_o;
  wire [47:0] n1271_o;
  wire [95:0] n1272_o;
  wire n1274_o;
  wire [95:0] n1275_o;
  wire [47:0] n1282_o;
  wire [47:0] n1285_o;
  wire [95:0] n1286_o;
  wire n1288_o;
  wire [95:0] n1289_o;
  wire [47:0] n1296_o;
  wire [47:0] n1299_o;
  wire [95:0] n1300_o;
  wire n1302_o;
  wire [95:0] n1303_o;
  wire [47:0] n1310_o;
  wire [47:0] n1313_o;
  wire [95:0] n1314_o;
  reg [17:0] n1317_q = 0;
  reg [2:0] n1318_q = 0;
  reg [5:0] n1319_q = 0;
  reg [5:0] n1320_q = 0;
  reg [5:0] n1321_q = 0;
  reg [2:0] n1322_q = 0;
  reg n1323_q = 0;
  reg [31:0] n1324_q = 0;
  reg [31:0] n1325_q = 0;
  reg [31:0] n1326_q = 0;
  reg [31:0] n1327_q = 0;
  reg [31:0] n1328_q = 0;
  reg [31:0] n1329_q = 0;
  reg [95:0] n1330_q = 0;
  assign rddata_re = n1140_o;
  assign rddata_im = n1141_o;
  assign romaddr = romaddr0;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:21:17  */
  assign n1140_o = outdata[47:0];
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:51:42  */
  assign n1141_o = outdata[95:48];
  /* ../fpga-fft/rtl/twiddle_generator.vhd:39:16  */
  assign romdata1 = n1317_q; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:40:16  */
  always @*
    romaddr0 = n1318_q; // (isignal)
  initial
    romaddr0 = 3'b000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:40:25  */
  always @*
    romaddrnext = n1156_o; // (isignal)
  initial
    romaddrnext = 3'b000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:41:16  */
  always @*
    phase = n1319_q; // (isignal)
  initial
    phase = 6'b000000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:41:22  */
  always @*
    phase1 = sr_dout; // (isignal)
  initial
    phase1 = 6'b000000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:41:29  */
  always @*
    phase2 = n1320_q; // (isignal)
  initial
    phase2 = 6'b000000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:41:36  */
  always @*
    phase3 = n1321_q; // (isignal)
  initial
    phase3 = 6'b000000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:42:16  */
  always @*
    ph3 = n1193_o; // (isignal)
  initial
    ph3 = 3'b000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:42:20  */
  always @*
    ph4 = n1322_q; // (isignal)
  initial
    ph4 = 3'b000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:43:16  */
  assign iszero = n1323_q; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:43:23  */
  assign iszeronext = n1171_o; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:45:16  */
  assign re = n1324_q; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:45:19  */
  assign im = n1325_q; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:45:22  */
  assign re0 = n1178_o; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:45:26  */
  assign im0 = n1183_o; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:45:31  */
  assign re_p = n1326_q; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:45:37  */
  assign re_m = n1327_q; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:45:43  */
  assign im_p = n1328_q; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:45:49  */
  assign im_m = n1329_q; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:46:16  */
  assign outdata = n1330_q; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:46:25  */
  assign outdata0 = n1219_o; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:51:30  */
  assign n1151_o = rdaddr[2:0];
  /* ../fpga-fft/rtl/twiddle_generator.vhd:51:53  */
  assign n1153_o = n1151_o - 3'b001;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:51:67  */
  assign n1154_o = rdaddr[3];
  /* ../fpga-fft/rtl/twiddle_generator.vhd:51:81  */
  assign n1155_o = ~n1154_o;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:51:56  */
  assign n1156_o = n1155_o ? n1153_o : n1158_o;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:52:49  */
  assign n1157_o = rdaddr[2:0];
  /* ../fpga-fft/rtl/twiddle_generator.vhd:52:39  */
  assign n1158_o = ~n1157_o;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:60:9  */
  sr_unsigned_6_2 sr (
    .clk(clk),
    .din(phase),
    .ce(n1164_o),
    .dout(sr_dout));
  /* ../fpga-fft/rtl/twiddle_generator.vhd:63:38  */
  assign n1168_o = phase1[3:0];
  /* ../fpga-fft/rtl/twiddle_generator.vhd:63:61  */
  assign n1170_o = n1168_o == 4'b0000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:63:27  */
  assign n1171_o = n1170_o ? 1'b1 : 1'b0;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:68:20  */
  assign n1178_o = iszero ? 32'b00000000000000000000001000000000 : n1181_o;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:69:45  */
  assign n1179_o = romdata1[8:0];
  /* ../fpga-fft/rtl/twiddle_generator.vhd:69:17  */
  assign n1180_o = {22'b0, n1179_o};  //  uext
  /* ../fpga-fft/rtl/twiddle_generator.vhd:69:17  */
  assign n1181_o = {1'b0, n1180_o};  //  uext
  /* ../fpga-fft/rtl/twiddle_generator.vhd:70:18  */
  assign n1183_o = iszero ? 32'b00000000000000000000000000000000 : n1186_o;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:71:45  */
  assign n1184_o = romdata1[17:9];
  /* ../fpga-fft/rtl/twiddle_generator.vhd:71:17  */
  assign n1185_o = {22'b0, n1184_o};  //  uext
  /* ../fpga-fft/rtl/twiddle_generator.vhd:71:17  */
  assign n1186_o = {1'b0, n1185_o};  //  uext
  /* ../fpga-fft/rtl/twiddle_generator.vhd:75:22  */
  assign n1193_o = phase3[5:3];
  /* ../fpga-fft/rtl/twiddle_generator.vhd:79:17  */
  assign n1196_o = -re;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:81:17  */
  assign n1201_o = -im;
  /* ../fpga-fft/rtl/fft_types.vhd:131:27  */
  assign n1212_o = {{16{re_p[31]}}, re_p}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:132:27  */
  assign n1215_o = {{16{im_p[31]}}, im_p}; // sext
  assign n1216_o = {n1215_o, n1212_o};
  /* ../fpga-fft/rtl/twiddle_generator.vhd:96:65  */
  assign n1218_o = ph4 == 3'b000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:96:57  */
  assign n1219_o = n1218_o ? n1216_o : n1233_o;
  /* ../fpga-fft/rtl/fft_types.vhd:131:27  */
  assign n1226_o = {{16{im_p[31]}}, im_p}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:132:27  */
  assign n1229_o = {{16{re_p[31]}}, re_p}; // sext
  assign n1230_o = {n1229_o, n1226_o};
  /* ../fpga-fft/rtl/twiddle_generator.vhd:97:73  */
  assign n1232_o = ph4 == 3'b001;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:96:68  */
  assign n1233_o = n1232_o ? n1230_o : n1247_o;
  /* ../fpga-fft/rtl/fft_types.vhd:131:27  */
  assign n1240_o = {{16{im_m[31]}}, im_m}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:132:27  */
  assign n1243_o = {{16{re_p[31]}}, re_p}; // sext
  assign n1244_o = {n1243_o, n1240_o};
  /* ../fpga-fft/rtl/twiddle_generator.vhd:98:73  */
  assign n1246_o = ph4 == 3'b010;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:97:76  */
  assign n1247_o = n1246_o ? n1244_o : n1261_o;
  /* ../fpga-fft/rtl/fft_types.vhd:131:27  */
  assign n1254_o = {{16{re_m[31]}}, re_m}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:132:27  */
  assign n1257_o = {{16{im_p[31]}}, im_p}; // sext
  assign n1258_o = {n1257_o, n1254_o};
  /* ../fpga-fft/rtl/twiddle_generator.vhd:99:73  */
  assign n1260_o = ph4 == 3'b011;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:98:76  */
  assign n1261_o = n1260_o ? n1258_o : n1275_o;
  /* ../fpga-fft/rtl/fft_types.vhd:131:27  */
  assign n1268_o = {{16{re_m[31]}}, re_m}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:132:27  */
  assign n1271_o = {{16{im_m[31]}}, im_m}; // sext
  assign n1272_o = {n1271_o, n1268_o};
  /* ../fpga-fft/rtl/twiddle_generator.vhd:100:73  */
  assign n1274_o = ph4 == 3'b100;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:99:76  */
  assign n1275_o = n1274_o ? n1272_o : n1289_o;
  /* ../fpga-fft/rtl/fft_types.vhd:131:27  */
  assign n1282_o = {{16{im_m[31]}}, im_m}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:132:27  */
  assign n1285_o = {{16{re_m[31]}}, re_m}; // sext
  assign n1286_o = {n1285_o, n1282_o};
  /* ../fpga-fft/rtl/twiddle_generator.vhd:101:73  */
  assign n1288_o = ph4 == 3'b101;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:100:76  */
  assign n1289_o = n1288_o ? n1286_o : n1303_o;
  /* ../fpga-fft/rtl/fft_types.vhd:131:27  */
  assign n1296_o = {{16{im_p[31]}}, im_p}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:132:27  */
  assign n1299_o = {{16{re_m[31]}}, re_m}; // sext
  assign n1300_o = {n1299_o, n1296_o};
  /* ../fpga-fft/rtl/twiddle_generator.vhd:102:73  */
  assign n1302_o = ph4 == 3'b110;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:101:76  */
  assign n1303_o = n1302_o ? n1300_o : n1314_o;
  /* ../fpga-fft/rtl/fft_types.vhd:131:27  */
  assign n1310_o = {{16{re_p[31]}}, re_p}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:132:27  */
  assign n1313_o = {{16{im_m[31]}}, im_m}; // sext
  assign n1314_o = {n1313_o, n1310_o};
  /* ../fpga-fft/rtl/twiddle_generator.vhd:65:29  */
  always @(posedge clk)
    n1317_q <= romdata;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:53:33  */
  always @(posedge clk)
    n1318_q <= romaddrnext;
  initial
    n1318_q = 3'b000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:54:25  */
  always @(posedge clk)
    n1319_q <= rdaddr;
  initial
    n1319_q = 6'b000000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:62:26  */
  always @(posedge clk)
    n1320_q <= phase1;
  initial
    n1320_q = 6'b000000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:74:26  */
  always @(posedge clk)
    n1321_q <= phase2;
  initial
    n1321_q = 6'b000000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:82:20  */
  always @(posedge clk)
    n1322_q <= ph3;
  initial
    n1322_q = 3'b000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:64:30  */
  always @(posedge clk)
    n1323_q <= iszeronext;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:72:19  */
  always @(posedge clk)
    n1324_q <= re0;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:73:19  */
  always @(posedge clk)
    n1325_q <= im0;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:78:20  */
  always @(posedge clk)
    n1326_q <= re;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:79:21  */
  always @(posedge clk)
    n1327_q <= n1196_o;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:80:20  */
  always @(posedge clk)
    n1328_q <= im;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:81:21  */
  always @(posedge clk)
    n1329_q <= n1201_o;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:106:29  */
  always @(posedge clk)
    n1330_q <= outdata0;
endmodule

module twiddleaddrgen_4_2_7_9159cb8bcee7fcb95582f140960cdae72788d326
  (input  clk,
   input  [5:0] phase,
   input  [3:0] bitpermout,
   output [5:0] twaddr,
   output [3:0] bitpermin);
  reg [5:0] ph0 = 0;
  reg [5:0] ph_twiddle = 0;
  reg [3:0] twmajoraddr = 0;
  reg [5:0] twaddr0 = 0;
  reg [5:0] twaddr0next = 0;
  wire [5:0] n1112_o;
  wire [5:0] n1114_o;
  wire [3:0] n1117_o;
  wire [3:0] n1119_o;
  wire [3:0] n1120_o;
  wire [1:0] n1122_o;
  wire n1124_o;
  wire [5:0] n1125_o;
  wire [4:0] n1127_o;
  wire [5:0] n1128_o;
  wire [5:0] n1129_o;
  wire n1130_o;
  wire [5:0] n1131_o;
  wire [5:0] n1132_o;
  wire [5:0] n1133_o;
  reg [5:0] n1136_q = 0;
  reg [5:0] n1138_q = 0;
  assign twaddr = twaddr0;
  assign bitpermin = n1117_o;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:36:22  */
  always @*
    ph0 = phase; // (isignal)
  initial
    ph0 = 6'b000000;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:38:16  */
  always @*
    ph_twiddle = n1136_q; // (isignal)
  initial
    ph_twiddle = 6'b000000;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:39:16  */
  always @*
    twmajoraddr = n1119_o; // (isignal)
  initial
    twmajoraddr = 4'b0000;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:41:16  */
  always @*
    twaddr0 = n1138_q; // (isignal)
  initial
    twaddr0 = 6'b000000;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:41:25  */
  always @*
    twaddr0next = n1125_o; // (isignal)
  initial
    twaddr0next = 6'b000000;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:51:26  */
  assign n1112_o = ph0 + 6'b000111;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:51:39  */
  assign n1114_o = n1112_o + 6'b000010;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:53:32  */
  assign n1117_o = ph_twiddle[5:2];
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:54:35  */
  assign n1119_o = 1'b1 ? bitpermout : n1120_o;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:55:27  */
  assign n1120_o = ph_twiddle[5:2];
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:62:61  */
  assign n1122_o = ph_twiddle[1:0];
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:62:83  */
  assign n1124_o = n1122_o == 2'b00;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:62:46  */
  assign n1125_o = n1124_o ? 6'b000000 : n1131_o;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:63:64  */
  assign n1127_o = {twmajoraddr, 1'b0};
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:63:49  */
  assign n1128_o = {1'b0, n1127_o};  //  uext
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:63:49  */
  assign n1129_o = twaddr0 + n1128_o;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:63:86  */
  assign n1130_o = ph_twiddle[0];
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:62:86  */
  assign n1131_o = n1130_o ? n1129_o : n1133_o;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:64:49  */
  assign n1132_o = {2'b0, twmajoraddr};  //  uext
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:64:49  */
  assign n1133_o = twaddr0 - n1132_o;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:51:42  */
  always @(posedge clk)
    n1136_q <= n1114_o;
  initial
    n1136_q = 6'b000000;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:66:32  */
  always @(posedge clk)
    n1138_q <= twaddr0next;
  initial
    n1138_q = 6'b000000;
endmodule

module transposer_2_4_8
  (input  clk,
   input  [47:0] din_re,
   input  [47:0] din_im,
   input  [5:0] phase,
   input  reorderenable,
   output [47:0] dout_re,
   output [47:0] dout_im);
  wire [95:0] n1084_o;
  wire [47:0] n1086_o;
  wire [47:0] n1087_o;
  wire [95:0] din2;
  wire [95:0] dout0;
  wire [95:0] dout1;
  wire [5:0] iaddr;
  wire [5:0] iaddr2;
  wire [5:0] oaddr;
  wire [5:0] gb_addrgen_addr;
  wire [47:0] gb_g3_ram_rddata_re;
  wire [47:0] gb_g3_ram_rddata_im;
  wire [95:0] n1089_o;
  localparam n1091_o = 1'b1;
  wire [47:0] n1092_o;
  wire [47:0] n1093_o;
  wire [5:0] gb_sr1_dout;
  localparam n1095_o = 1'b1;
  reg [95:0] n1100_q = 0;
  reg [5:0] n1101_q = 0;
  assign dout_re = n1086_o;
  assign dout_im = n1087_o;
  /* ../fpga-fft/rtl/fft_types.vhd:52:14  */
  assign n1084_o = {din_im, din_re};
  assign n1086_o = dout1[47:0];
  /* ../fpga-fft/rtl/fft_types.vhd:137:26  */
  assign n1087_o = dout1[95:48];
  /* ../fpga-fft/rtl/transposer.vhd:31:16  */
  assign din2 = n1100_q; // (signal)
  /* ../fpga-fft/rtl/transposer.vhd:31:22  */
  assign dout0 = n1089_o; // (signal)
  /* ../fpga-fft/rtl/transposer.vhd:31:29  */
  assign dout1 = dout0; // (signal)
  /* ../fpga-fft/rtl/transposer.vhd:32:16  */
  assign iaddr = gb_sr1_dout; // (signal)
  /* ../fpga-fft/rtl/transposer.vhd:32:23  */
  assign iaddr2 = n1101_q; // (signal)
  /* ../fpga-fft/rtl/transposer.vhd:32:31  */
  assign oaddr = gb_addrgen_addr; // (signal)
  /* ../fpga-fft/rtl/transposer.vhd:47:17  */
  transposer_addrgen_2_4_2 gb_addrgen (
    .clk(clk),
    .reorderenable(reorderenable),
    .phase(phase),
    .addr(gb_addrgen_addr));
  /* ../fpga-fft/rtl/transposer.vhd:52:25  */
  complexramlut_8_6 gb_g3_ram (
    .rdclk(clk),
    .wrclk(clk),
    .rdaddr(oaddr),
    .wren(n1091_o),
    .wraddr(iaddr2),
    .wrdata_re(n1092_o),
    .wrdata_im(n1093_o),
    .rddata_re(gb_g3_ram_rddata_re),
    .rddata_im(gb_g3_ram_rddata_im));
  assign n1089_o = {gb_g3_ram_rddata_im, gb_g3_ram_rddata_re};
  assign n1092_o = din2[47:0];
  assign n1093_o = din2[95:48];
  /* ../fpga-fft/rtl/transposer.vhd:78:17  */
  sr_unsigned_6_2 gb_sr1 (
    .clk(clk),
    .din(oaddr),
    .ce(n1095_o),
    .dout(gb_sr1_dout));
  /* ../fpga-fft/rtl/transposer.vhd:80:29  */
  always @(posedge clk)
    n1100_q <= n1084_o;
  /* ../fpga-fft/rtl/transposer.vhd:81:33  */
  always @(posedge clk)
    n1101_q <= iaddr;
endmodule

module sr_unsigned_6_2
  (input  clk,
   input  [5:0] din,
   input  ce,
   output [5:0] dout);
  wire [17:0] arr;
  wire [5:0] n1072_o;
  wire n1073_o;
  wire n1074_o;
  wire [5:0] n1075_o;
  wire [5:0] n1076_o;
  wire [5:0] n1077_o;
  wire n1078_o;
  wire n1079_o;
  wire [5:0] n1080_o;
  wire [5:0] n1081_o;
  wire [5:0] n1082_o;
  wire [17:0] n1083_o;
  assign dout = n1082_o;
  /* ../fpga-fft/rtl/sr.vhd:43:16  */
  assign arr = n1083_o; // (signal)
  /* ../fpga-fft/rtl/sr.vhd:46:30  */
  assign n1072_o = arr[11:6];
  /* ../fpga-fft/rtl/sr.vhd:46:52  */
  assign n1073_o = 1'b0; // posedge
  /* ../fpga-fft/rtl/sr.vhd:46:48  */
  assign n1074_o = ce & n1073_o;
  /* ../fpga-fft/rtl/sr.vhd:46:36  */
  assign n1075_o = n1074_o ? n1072_o : n1076_o;
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:69:9  */
  assign n1076_o = arr[5:0];
  /* ../fpga-fft/rtl/sr.vhd:46:30  */
  assign n1077_o = arr[17:12];
  /* ../fpga-fft/rtl/sr.vhd:46:52  */
  assign n1078_o = 1'b0; // posedge
  /* ../fpga-fft/rtl/sr.vhd:46:48  */
  assign n1079_o = ce & n1078_o;
  /* ../fpga-fft/rtl/sr.vhd:46:36  */
  assign n1080_o = n1079_o ? n1077_o : n1081_o;
  /* ../fpga-fft/rtl/fft_types.vhd:52:14  */
  assign n1081_o = arr[11:6];
  /* ../fpga-fft/rtl/sr.vhd:49:20  */
  assign n1082_o = arr[5:0];
  assign n1083_o = {din, n1080_o, n1075_o};
endmodule

module complexramlut_8_6
  (input  rdclk,
   input  wrclk,
   input  [5:0] rdaddr,
   input  wren,
   input  [5:0] wraddr,
   input  [47:0] wrdata_re,
   input  [47:0] wrdata_im,
   output [47:0] rddata_re,
   output [47:0] rddata_im);
  wire [47:0] n1015_o;
  wire [47:0] n1016_o;
  wire [95:0] n1017_o;
  wire [5:0] rdaddr1;
  wire [15:0] wrdata1;
  wire [15:0] tmpdata;
  reg [7:0] tmpdata1 = 0;
  reg [7:0] tmpdata2 = 0;
  wire [7:0] n1025_o;
  wire [7:0] n1028_o;
  wire [47:0] n1037_o;
  wire [47:0] n1040_o;
  wire [95:0] n1041_o;
  wire [7:0] n1047_o;
  wire [7:0] n1053_o;
  wire [15:0] n1054_o;
  reg [5:0] n1066_q = 0;
  reg [7:0] n1067_q = 0;
  reg [7:0] n1068_q = 0;
  wire [15:0] n1069_data; // mem_rd
  assign rddata_re = n1015_o;
  assign rddata_im = n1016_o;
  assign n1015_o = n1041_o[47:0];
  assign n1016_o = n1041_o[95:48];
  assign n1017_o = {wrdata_im, wrdata_re};
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:41:16  */
  assign rdaddr1 = n1066_q; // (signal)
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:42:16  */
  assign wrdata1 = n1054_o; // (signal)
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:44:16  */
  assign tmpdata = n1069_data; // (signal)
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:45:16  */
  always @*
    tmpdata1 = n1067_q; // (isignal)
  initial
    tmpdata1 = 8'b00000000;
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:45:25  */
  always @*
    tmpdata2 = n1068_q; // (isignal)
  initial
    tmpdata2 = 8'b00000000;
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:60:35  */
  assign n1025_o = tmpdata[7:0];
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:61:35  */
  assign n1028_o = tmpdata[15:8];
  /* ../fpga-fft/rtl/fft_types.vhd:139:27  */
  assign n1037_o = {{40{tmpdata1[7]}}, tmpdata1}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:140:27  */
  assign n1040_o = {{40{tmpdata2[7]}}, tmpdata2}; // sext
  assign n1041_o = {n1040_o, n1037_o};
  /* ../fpga-fft/rtl/fft_types.vhd:150:30  */
  assign n1047_o = n1017_o[55:48];
  /* ../fpga-fft/rtl/fft_types.vhd:146:30  */
  assign n1053_o = n1017_o[7:0];
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:67:25  */
  assign n1054_o = {n1047_o, n1053_o};
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:54:27  */
  always @(posedge rdclk)
    n1066_q <= rdaddr;
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:60:58  */
  always @(posedge rdclk)
    n1067_q <= n1025_o;
  initial
    n1067_q = 8'b00000000;
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:61:62  */
  always @(posedge rdclk)
    n1068_q <= n1028_o;
  initial
    n1068_q = 8'b00000000;
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:24:25  */
  reg [15:0] ram1[63:0] ; // memor = 0;
  assign n1069_data = ram1[rdaddr1];
  always @(posedge wrclk)
    if (wren)
      ram1[wraddr] <= wrdata1;
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:58:25  */
  /* ../fpga-fft/rtl/complex_ram_lut.vhd:73:46  */
endmodule

module sr_unsigned_12_2
  (input  clk,
   input  [11:0] din,
   input  ce,
   output [11:0] dout);
  wire [35:0] arr;
  wire [11:0] n1002_o;
  wire n1003_o;
  wire n1004_o;
  wire [11:0] n1005_o;
  wire [11:0] n1006_o;
  wire [11:0] n1007_o;
  wire n1008_o;
  wire n1009_o;
  wire [11:0] n1010_o;
  wire [11:0] n1011_o;
  wire [11:0] n1012_o;
  wire [35:0] n1013_o;
  assign dout = n1012_o;
  /* ../fpga-fft/rtl/sr.vhd:43:16  */
  assign arr = n1013_o; // (signal)
  /* ../fpga-fft/rtl/sr.vhd:46:30  */
  assign n1002_o = arr[23:12];
  /* ../fpga-fft/rtl/sr.vhd:46:52  */
  assign n1003_o = 1'b0; // posedge
  /* ../fpga-fft/rtl/sr.vhd:46:48  */
  assign n1004_o = ce & n1003_o;
  /* ../fpga-fft/rtl/sr.vhd:46:36  */
  assign n1005_o = n1004_o ? n1002_o : n1006_o;
  assign n1006_o = arr[11:0];
  /* ../fpga-fft/rtl/sr.vhd:46:30  */
  assign n1007_o = arr[35:24];
  /* ../fpga-fft/rtl/sr.vhd:46:52  */
  assign n1008_o = 1'b0; // posedge
  /* ../fpga-fft/rtl/sr.vhd:46:48  */
  assign n1009_o = ce & n1008_o;
  /* ../fpga-fft/rtl/sr.vhd:46:36  */
  assign n1010_o = n1009_o ? n1007_o : n1011_o;
  assign n1011_o = arr[23:12];
  /* ../fpga-fft/rtl/sr.vhd:49:20  */
  assign n1012_o = arr[11:0];
  assign n1013_o = {din, n1010_o, n1005_o};
endmodule

module multiplyadd_11_8_19_bf8b4530d8d246dd74ac53a13471bba17941dff7
  (input  clk,
   input  [10:0] a,
   input  [7:0] b,
   input  [18:0] c,
   output [18:0] p);
  wire [10:0] a1;
  wire [7:0] b1;
  wire [18:0] m0;
  wire [18:0] m;
  wire [18:0] n989_o;
  wire [18:0] n990_o;
  wire [18:0] n991_o;
  wire [18:0] n994_o;
  reg [10:0] n997_q = 0;
  reg [7:0] n998_q = 0;
  reg [18:0] n999_q = 0;
  reg [18:0] n1000_q = 0;
  assign p = n1000_q;
  /* ../fpga-fft/rtl/multiply_add.vhd:21:16  */
  assign a1 = n997_q; // (signal)
  /* ../fpga-fft/rtl/multiply_add.vhd:22:16  */
  assign b1 = n998_q; // (signal)
  /* ../fpga-fft/rtl/multiply_add.vhd:23:16  */
  assign m0 = n999_q; // (signal)
  /* ../fpga-fft/rtl/multiply_add.vhd:24:16  */
  assign m = m0; // (signal)
  /* ../fpga-fft/rtl/multiply_add.vhd:28:17  */
  assign n989_o = {{8{a1[10]}}, a1}; // sext
  /* ../fpga-fft/rtl/multiply_add.vhd:28:17  */
  assign n990_o = {{11{b1[7]}}, b1}; // sext
  /* ../fpga-fft/rtl/multiply_add.vhd:28:17  */
  assign n991_o = n989_o * n990_o; // smul
  /* ../fpga-fft/rtl/multiply_add.vhd:31:23  */
  assign n994_o = c - m;
  /* ../fpga-fft/rtl/multiply_add.vhd:26:17  */
  always @(posedge clk)
    n997_q <= a;
  /* ../fpga-fft/rtl/multiply_add.vhd:27:17  */
  always @(posedge clk)
    n998_q <= b;
  /* ../fpga-fft/rtl/multiply_add.vhd:28:21  */
  always @(posedge clk)
    n999_q <= n991_o;
  /* ../fpga-fft/rtl/multiply_add.vhd:31:26  */
  always @(posedge clk)
    n1000_q <= n994_o;
endmodule

module multiplyadd_11_8_19_5ba93c9db0cff93f52b521d7420e43f6eda2784f
  (input  clk,
   input  [10:0] a,
   input  [7:0] b,
   input  [18:0] c,
   output [18:0] p);
  wire [10:0] a1;
  wire [7:0] b1;
  wire [18:0] m0;
  wire [18:0] m;
  wire [18:0] n972_o;
  wire [18:0] n973_o;
  wire [18:0] n974_o;
  wire [18:0] n977_o;
  reg [10:0] n980_q = 0;
  reg [7:0] n981_q = 0;
  reg [18:0] n982_q = 0;
  reg [18:0] n983_q = 0;
  assign p = n983_q;
  /* ../fpga-fft/rtl/multiply_add.vhd:21:16  */
  assign a1 = n980_q; // (signal)
  /* ../fpga-fft/rtl/multiply_add.vhd:22:16  */
  assign b1 = n981_q; // (signal)
  /* ../fpga-fft/rtl/multiply_add.vhd:23:16  */
  assign m0 = n982_q; // (signal)
  /* ../fpga-fft/rtl/multiply_add.vhd:24:16  */
  assign m = m0; // (signal)
  /* ../fpga-fft/rtl/multiply_add.vhd:28:17  */
  assign n972_o = {{8{a1[10]}}, a1}; // sext
  /* ../fpga-fft/rtl/multiply_add.vhd:28:17  */
  assign n973_o = {{11{b1[7]}}, b1}; // sext
  /* ../fpga-fft/rtl/multiply_add.vhd:28:17  */
  assign n974_o = n972_o * n973_o; // smul
  /* ../fpga-fft/rtl/multiply_add.vhd:34:23  */
  assign n977_o = m + c;
  /* ../fpga-fft/rtl/multiply_add.vhd:26:17  */
  always @(posedge clk)
    n980_q <= a;
  /* ../fpga-fft/rtl/multiply_add.vhd:27:17  */
  always @(posedge clk)
    n981_q <= b;
  /* ../fpga-fft/rtl/multiply_add.vhd:28:21  */
  always @(posedge clk)
    n982_q <= n974_o;
  /* ../fpga-fft/rtl/multiply_add.vhd:34:26  */
  always @(posedge clk)
    n983_q <= n977_o;
endmodule

module sr_unsigned_12_4
  (input  clk,
   input  [11:0] din,
   input  ce,
   output [11:0] dout);
  wire [59:0] arr;
  wire [11:0] n945_o;
  wire n946_o;
  wire n947_o;
  wire [11:0] n948_o;
  wire [11:0] n949_o;
  wire [11:0] n950_o;
  wire n951_o;
  wire n952_o;
  wire [11:0] n953_o;
  wire [11:0] n954_o;
  wire [11:0] n955_o;
  wire n956_o;
  wire n957_o;
  wire [11:0] n958_o;
  wire [11:0] n959_o;
  wire [11:0] n960_o;
  wire n961_o;
  wire n962_o;
  wire [11:0] n963_o;
  wire [11:0] n964_o;
  wire [11:0] n965_o;
  wire [59:0] n966_o;
  assign dout = n965_o;
  /* ../fpga-fft/rtl/sr.vhd:43:16  */
  assign arr = n966_o; // (signal)
  /* ../fpga-fft/rtl/sr.vhd:46:30  */
  assign n945_o = arr[23:12];
  /* ../fpga-fft/rtl/sr.vhd:46:52  */
  assign n946_o = 1'b0; // posedge
  /* ../fpga-fft/rtl/sr.vhd:46:48  */
  assign n947_o = ce & n946_o;
  /* ../fpga-fft/rtl/sr.vhd:46:36  */
  assign n948_o = n947_o ? n945_o : n949_o;
  assign n949_o = arr[11:0];
  /* ../fpga-fft/rtl/sr.vhd:46:30  */
  assign n950_o = arr[35:24];
  /* ../fpga-fft/rtl/sr.vhd:46:52  */
  assign n951_o = 1'b0; // posedge
  /* ../fpga-fft/rtl/sr.vhd:46:48  */
  assign n952_o = ce & n951_o;
  /* ../fpga-fft/rtl/sr.vhd:46:36  */
  assign n953_o = n952_o ? n950_o : n954_o;
  assign n954_o = arr[23:12];
  /* ../fpga-fft/rtl/sr.vhd:46:30  */
  assign n955_o = arr[47:36];
  /* ../fpga-fft/rtl/sr.vhd:46:52  */
  assign n956_o = 1'b0; // posedge
  /* ../fpga-fft/rtl/sr.vhd:46:48  */
  assign n957_o = ce & n956_o;
  /* ../fpga-fft/rtl/sr.vhd:46:36  */
  assign n958_o = n957_o ? n955_o : n959_o;
  assign n959_o = arr[35:24];
  /* ../fpga-fft/rtl/sr.vhd:46:30  */
  assign n960_o = arr[59:48];
  /* ../fpga-fft/rtl/sr.vhd:46:52  */
  assign n961_o = 1'b0; // posedge
  /* ../fpga-fft/rtl/sr.vhd:46:48  */
  assign n962_o = ce & n961_o;
  /* ../fpga-fft/rtl/sr.vhd:46:36  */
  assign n963_o = n962_o ? n960_o : n964_o;
  assign n964_o = arr[47:36];
  /* ../fpga-fft/rtl/sr.vhd:49:20  */
  assign n965_o = arr[11:0];
  assign n966_o = {din, n963_o, n958_o, n953_o, n948_o};
endmodule

module transposer_addrgen_6_6_4
  (input  clk,
   input  reorderenable,
   input  [11:0] phase,
   output [11:0] addr);
  wire [11:0] ph1;
  wire [11:0] ph2;
  wire [11:0] ph3;
  reg [3:0] state = 0;
  reg [3:0] statenext = 0;
  wire [11:0] n905_o;
  wire [11:0] n907_o;
  wire [3:0] n913_o;
  wire [3:0] n915_o;
  wire n917_o;
  wire [3:0] n918_o;
  wire [3:0] n920_o;
  wire n922_o;
  wire n923_o;
  wire [30:0] n927_o;
  reg [11:0] n933_q = 0;
  reg [11:0] n934_q = 0;
  reg [11:0] n935_q = 0;
  wire [3:0] n936_o;
  reg [3:0] n937_q = 0;
  reg [11:0] n938_q = 0;
  wire [11:0] n939_o;
  wire [3:0] n941_o;
  wire [11:0] n942_o;
  wire [11:0] n943_o;
  assign addr = n938_q;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:21:16  */
  assign ph1 = n933_q; // (signal)
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:21:20  */
  assign ph2 = n934_q; // (signal)
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:21:24  */
  assign ph3 = n935_q; // (signal)
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:33:16  */
  always @*
    state = n937_q; // (isignal)
  initial
    state = 4'b0000;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:33:22  */
  always @*
    statenext = n918_o; // (isignal)
  initial
    statenext = 4'b0000;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:35:21  */
  assign n905_o = phase + 12'b000000000100;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:35:34  */
  assign n907_o = n905_o + 12'b000000000100;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:39:27  */
  assign n913_o = state + 4'b0110;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:39:30  */
  assign n915_o = n913_o - 4'b1100;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:39:52  */
  assign n917_o = $unsigned(state) >= $unsigned(4'b0110);
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:39:42  */
  assign n918_o = n917_o ? n915_o : n920_o;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:39:80  */
  assign n920_o = state + 4'b0110;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:40:36  */
  assign n922_o = ph1 == 12'b000000000000;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:40:39  */
  assign n923_o = n922_o & reorderenable;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:51:41  */
  assign n927_o = {27'b0, state};  //  uext
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:35:41  */
  always @(posedge clk)
    n933_q <= n907_o;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:38:20  */
  always @(posedge clk)
    n934_q <= ph1;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:51:60  */
  always @(posedge clk)
    n935_q <= n943_o;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:40:28  */
  assign n936_o = n923_o ? statenext : state;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:40:28  */
  always @(posedge clk)
    n937_q <= n936_o;
  initial
    n937_q = 4'b0000;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:56:29  */
  always @(posedge clk)
    n938_q <= ph3;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:51:24  */
  assign n939_o = ph2 << n927_o;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:51:24  */
  assign n941_o = 4'b1100 - state;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:51:24  */
  assign n942_o = ph2 >> n941_o;
  /* ../fpga-fft/rtl/transposer_addr_gen.vhd:51:24  */
  assign n943_o = n939_o | n942_o;
endmodule

module sr_unsigned_12_3
  (input  clk,
   input  [11:0] din,
   input  ce,
   output [11:0] dout);
  wire [47:0] arr;
  wire [11:0] n884_o;
  wire n885_o;
  wire n886_o;
  wire [11:0] n887_o;
  wire [11:0] n888_o;
  wire [11:0] n889_o;
  wire n890_o;
  wire n891_o;
  wire [11:0] n892_o;
  wire [11:0] n893_o;
  wire [11:0] n894_o;
  wire n895_o;
  wire n896_o;
  wire [11:0] n897_o;
  wire [11:0] n898_o;
  wire [11:0] n899_o;
  wire [47:0] n900_o;
  assign dout = n899_o;
  /* ../fpga-fft/rtl/sr.vhd:43:16  */
  assign arr = n900_o; // (signal)
  /* ../fpga-fft/rtl/sr.vhd:46:30  */
  assign n884_o = arr[23:12];
  /* ../fpga-fft/rtl/sr.vhd:46:52  */
  assign n885_o = 1'b0; // posedge
  /* ../fpga-fft/rtl/sr.vhd:46:48  */
  assign n886_o = ce & n885_o;
  /* ../fpga-fft/rtl/sr.vhd:46:36  */
  assign n887_o = n886_o ? n884_o : n888_o;
  /* ../fpga-fft/rtl/complex_ram.vhd:59:9  */
  assign n888_o = arr[11:0];
  /* ../fpga-fft/rtl/sr.vhd:46:30  */
  assign n889_o = arr[35:24];
  /* ../fpga-fft/rtl/sr.vhd:46:52  */
  assign n890_o = 1'b0; // posedge
  /* ../fpga-fft/rtl/sr.vhd:46:48  */
  assign n891_o = ce & n890_o;
  /* ../fpga-fft/rtl/sr.vhd:46:36  */
  assign n892_o = n891_o ? n889_o : n893_o;
  /* ../fpga-fft/rtl/fft_types.vhd:52:14  */
  assign n893_o = arr[23:12];
  /* ../fpga-fft/rtl/sr.vhd:46:30  */
  assign n894_o = arr[47:36];
  /* ../fpga-fft/rtl/sr.vhd:46:52  */
  assign n895_o = 1'b0; // posedge
  /* ../fpga-fft/rtl/sr.vhd:46:48  */
  assign n896_o = ce & n895_o;
  /* ../fpga-fft/rtl/sr.vhd:46:36  */
  assign n897_o = n896_o ? n894_o : n898_o;
  assign n898_o = arr[35:24];
  /* ../fpga-fft/rtl/sr.vhd:49:20  */
  assign n899_o = arr[11:0];
  assign n900_o = {din, n897_o, n892_o, n887_o};
endmodule

module complexram_8_12
  (input  rdclk,
   input  wrclk,
   input  [11:0] rdaddr,
   input  wren,
   input  [11:0] wraddr,
   input  [47:0] wrdata_re,
   input  [47:0] wrdata_im,
   output [47:0] rddata_re,
   output [47:0] rddata_im);
  wire [47:0] n825_o;
  wire [47:0] n826_o;
  wire [95:0] n827_o;
  wire [11:0] rdaddr1;
  wire [15:0] wrdata1;
  wire [15:0] tmpdata;
  wire [7:0] tmpdata1;
  wire [7:0] tmpdata2;
  wire [7:0] n836_o;
  wire [7:0] n839_o;
  wire [47:0] n848_o;
  wire [47:0] n851_o;
  wire [95:0] n852_o;
  wire [7:0] n858_o;
  wire [7:0] n864_o;
  wire [15:0] n865_o;
  reg [7:0] n878_q = 0;
  reg [7:0] n879_q = 0;
  reg [15:0] n881_data; // mem_r = 0;
  assign rddata_re = n825_o;
  assign rddata_im = n826_o;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:38:17  */
  assign n825_o = n852_o[47:0];
  /* ../fpga-fft/rtl/reorder_buffer.vhd:37:17  */
  assign n826_o = n852_o[95:48];
  /* ../fpga-fft/rtl/reorder_buffer.vhd:34:17  */
  assign n827_o = {wrdata_im, wrdata_re};
  /* ../fpga-fft/rtl/complex_ram.vhd:32:16  */
  assign rdaddr1 = rdaddr; // (signal)
  /* ../fpga-fft/rtl/complex_ram.vhd:33:16  */
  assign wrdata1 = n865_o; // (signal)
  /* ../fpga-fft/rtl/complex_ram.vhd:35:16  */
  assign tmpdata = n881_data; // (signal)
  /* ../fpga-fft/rtl/complex_ram.vhd:36:16  */
  assign tmpdata1 = n878_q; // (signal)
  /* ../fpga-fft/rtl/complex_ram.vhd:36:25  */
  assign tmpdata2 = n879_q; // (signal)
  /* ../fpga-fft/rtl/complex_ram.vhd:50:35  */
  assign n836_o = tmpdata[7:0];
  /* ../fpga-fft/rtl/complex_ram.vhd:51:35  */
  assign n839_o = tmpdata[15:8];
  /* ../fpga-fft/rtl/fft_types.vhd:139:27  */
  assign n848_o = {{40{tmpdata1[7]}}, tmpdata1}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:140:27  */
  assign n851_o = {{40{tmpdata2[7]}}, tmpdata2}; // sext
  assign n852_o = {n851_o, n848_o};
  /* ../fpga-fft/rtl/fft_types.vhd:150:30  */
  assign n858_o = n827_o[55:48];
  /* ../fpga-fft/rtl/fft_types.vhd:146:30  */
  assign n864_o = n827_o[7:0];
  /* ../fpga-fft/rtl/complex_ram.vhd:57:25  */
  assign n865_o = {n858_o, n864_o};
  /* ../fpga-fft/rtl/complex_ram.vhd:50:58  */
  always @(posedge rdclk)
    n878_q <= n836_o;
  /* ../fpga-fft/rtl/complex_ram.vhd:51:62  */
  always @(posedge rdclk)
    n879_q <= n839_o;
  /* ../fpga-fft/rtl/complex_ram.vhd:15:25  */
  reg [15:0] ram1[4095:0] ; // memor = 0;
  always @(posedge rdclk)
    if (1'b1)
      n881_data <= ram1[rdaddr1];
  always @(posedge wrclk)
    if (wren)
      ram1[wraddr] <= wrdata1;
  /* ../fpga-fft/rtl/complex_ram.vhd:63:46  */
endmodule

module reorderbuffer_12_8_2_0_0
  (input  clk,
   input  [47:0] din_re,
   input  [47:0] din_im,
   input  [11:0] phase,
   input  [11:0] bitpermout,
   output [47:0] dout_re,
   output [47:0] dout_im,
   output [11:0] bitpermin,
   output bitpermcount);
  wire [95:0] n773_o;
  wire [47:0] n775_o;
  wire [47:0] n776_o;
  wire [95:0] din2;
  wire [95:0] dout0;
  wire [11:0] iaddr;
  wire [11:0] iaddr2;
  wire [11:0] oaddr;
  reg state = 0;
  reg statenext = 0;
  wire [11:0] ph1;
  wire [11:0] ph2;
  wire [11:0] n782_o;
  wire [11:0] n784_o;
  wire n791_o;
  wire n792_o;
  wire n794_o;
  wire n796_o;
  wire [47:0] g4_ram_rddata_re;
  wire [47:0] g4_ram_rddata_im;
  wire [95:0] n802_o;
  localparam n804_o = 1'b1;
  wire [47:0] n805_o;
  wire [47:0] n806_o;
  wire [11:0] sr1_dout;
  localparam n810_o = 1'b1;
  reg [95:0] n815_q = 0;
  reg [11:0] n816_q = 0;
  reg [11:0] n817_q = 0;
  wire n818_o;
  reg n819_q = 0;
  reg [11:0] n820_q = 0;
  reg [11:0] n821_q = 0;
  reg [95:0] n823_q = 0;
  assign dout_re = n775_o;
  assign dout_im = n776_o;
  assign bitpermin = ph2;
  assign bitpermcount = state;
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:101:74  */
  assign n773_o = {din_im, din_re};
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:96:47  */
  assign n775_o = n823_q[47:0];
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:96:39  */
  assign n776_o = n823_q[95:48];
  /* ../fpga-fft/rtl/reorder_buffer.vhd:43:16  */
  assign din2 = n815_q; // (signal)
  /* ../fpga-fft/rtl/reorder_buffer.vhd:43:21  */
  assign dout0 = n802_o; // (signal)
  /* ../fpga-fft/rtl/reorder_buffer.vhd:44:16  */
  assign iaddr = sr1_dout; // (signal)
  /* ../fpga-fft/rtl/reorder_buffer.vhd:44:23  */
  assign iaddr2 = n816_q; // (signal)
  /* ../fpga-fft/rtl/reorder_buffer.vhd:44:31  */
  assign oaddr = n817_q; // (signal)
  /* ../fpga-fft/rtl/reorder_buffer.vhd:53:16  */
  always @*
    state = n819_q; // (isignal)
  initial
    state = 1'b0;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:53:22  */
  always @*
    statenext = n792_o; // (isignal)
  initial
    statenext = 1'b0;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:54:16  */
  assign ph1 = n820_q; // (signal)
  /* ../fpga-fft/rtl/reorder_buffer.vhd:54:20  */
  assign ph2 = n821_q; // (signal)
  /* ../fpga-fft/rtl/reorder_buffer.vhd:57:21  */
  assign n782_o = phase + 12'b000000000110;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:57:33  */
  assign n784_o = n782_o - 12'b000000000000;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:61:46  */
  assign n791_o = $unsigned(state) >= $unsigned(1'b1);
  /* ../fpga-fft/rtl/reorder_buffer.vhd:61:36  */
  assign n792_o = n791_o ? 1'b0 : n794_o;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:61:71  */
  assign n794_o = state + 1'b1;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:62:36  */
  assign n796_o = ph1 == 12'b000000000000;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:77:17  */
  complexram_8_12 g4_ram (
    .rdclk(clk),
    .wrclk(clk),
    .rdaddr(oaddr),
    .wren(n804_o),
    .wraddr(iaddr2),
    .wrdata_re(n805_o),
    .wrdata_im(n806_o),
    .rddata_re(g4_ram_rddata_re),
    .rddata_im(g4_ram_rddata_im));
  assign n802_o = {g4_ram_rddata_im, g4_ram_rddata_re};
  assign n805_o = din2[47:0];
  assign n806_o = din2[95:48];
  /* ../fpga-fft/rtl/reorder_buffer.vhd:96:9  */
  sr_unsigned_12_3 sr1 (
    .clk(clk),
    .din(oaddr),
    .ce(n810_o),
    .dout(sr1_dout));
  /* ../fpga-fft/rtl/reorder_buffer.vhd:98:21  */
  always @(posedge clk)
    n815_q <= n773_o;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:99:25  */
  always @(posedge clk)
    n816_q <= iaddr;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:67:29  */
  always @(posedge clk)
    n817_q <= bitpermout;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:62:28  */
  assign n818_o = n796_o ? statenext : state;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:62:28  */
  always @(posedge clk)
    n819_q <= n818_o;
  initial
    n819_q = 1'b0;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:57:48  */
  always @(posedge clk)
    n820_q <= n784_o;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:60:20  */
  always @(posedge clk)
    n821_q <= ph1;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:84:31  */
  always @(posedge clk)
    n823_q <= dout0;
endmodule

module fft4096_sub64_2_8_10_bf8b4530d8d246dd74ac53a13471bba17941dff7
  (input  clk,
   input  [47:0] din_re,
   input  [47:0] din_im,
   input  [5:0] phase,
   output [47:0] dout_re,
   output [47:0] dout_im);
  wire [95:0] n720_o;
  wire [47:0] n722_o;
  wire [47:0] n723_o;
  wire [95:0] sub1din;
  wire [95:0] sub1dout;
  wire [95:0] sub2din;
  wire [95:0] sub2dout;
  wire [3:0] sub1phase;
  wire [1:0] sub2phase;
  wire [5:0] ph1;
  wire [5:0] ph2;
  wire [5:0] ph3;
  wire [95:0] transpout;
  wire [3:0] bitpermin;
  wire [3:0] bitpermout;
  wire [5:0] twaddr;
  wire [95:0] twdata;
  wire [2:0] romaddr;
  wire [17:0] romdata;
  wire [3:0] n724_o;
  wire [5:0] n726_o;
  wire [5:0] n728_o;
  wire [47:0] transp_dout_re;
  wire [47:0] transp_dout_im;
  wire [47:0] n731_o;
  wire [47:0] n732_o;
  wire [95:0] n733_o;
  localparam n735_o = 1'b1;
  wire [5:0] twag_twaddr;
  wire [3:0] twag_bitpermin;
  wire [47:0] twmult_out1_re;
  wire [47:0] twmult_out1_im;
  wire [47:0] n738_o;
  wire [47:0] n739_o;
  wire [47:0] n740_o;
  wire [47:0] n741_o;
  wire [95:0] n742_o;
  wire [5:0] n745_o;
  wire [5:0] n747_o;
  wire [1:0] n750_o;
  wire n751_o;
  wire n752_o;
  wire [1:0] n753_o;
  wire n754_o;
  wire [2:0] n755_o;
  wire n756_o;
  wire [3:0] n757_o;
  wire [47:0] tw_rddata_re;
  wire [47:0] tw_rddata_im;
  wire [2:0] tw_romaddr;
  wire [95:0] n758_o;
  wire [17:0] rom_romdata;
  wire [47:0] sub1_dout_re;
  wire [47:0] sub1_dout_im;
  wire [47:0] n762_o;
  wire [47:0] n763_o;
  wire [95:0] n764_o;
  wire [47:0] sub2inst_dout_re;
  wire [47:0] sub2inst_dout_im;
  wire [47:0] n766_o;
  wire [47:0] n767_o;
  wire [95:0] n768_o;
  reg [5:0] n770_q = 0;
  reg [5:0] n771_q = 0;
  assign dout_re = n722_o;
  assign dout_im = n723_o;
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:101:74  */
  assign n720_o = {din_im, din_re};
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:96:47  */
  assign n722_o = sub2dout[47:0];
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:96:39  */
  assign n723_o = sub2dout[95:48];
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:30:16  */
  assign sub1din = n720_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:30:25  */
  assign sub1dout = n764_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:30:35  */
  assign sub2din = n742_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:30:44  */
  assign sub2dout = n768_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:31:16  */
  assign sub1phase = n724_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:32:16  */
  assign sub2phase = n750_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:46:16  */
  assign ph1 = n770_q; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:46:21  */
  assign ph2 = ph1; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:46:26  */
  assign ph3 = n771_q; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:47:22  */
  assign transpout = n733_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:48:16  */
  assign bitpermin = twag_bitpermin; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:48:26  */
  assign bitpermout = n757_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:51:16  */
  assign twaddr = twag_twaddr; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:52:16  */
  assign twdata = n758_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:54:16  */
  assign romaddr = tw_romaddr; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:55:16  */
  assign romdata = rom_romdata; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:59:27  */
  assign n724_o = phase[3:0];
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:61:21  */
  assign n726_o = phase - 6'b100011;
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:61:24  */
  assign n728_o = n726_o + 6'b000001;
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:63:9  */
  transposer_2_4_8 transp (
    .clk(clk),
    .din_re(n731_o),
    .din_im(n732_o),
    .phase(ph1),
    .reorderenable(n735_o),
    .dout_re(transp_dout_re),
    .dout_im(transp_dout_im));
  assign n731_o = sub1dout[47:0];
  assign n732_o = sub1dout[95:48];
  assign n733_o = {transp_dout_im, transp_dout_re};
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:69:9  */
  twiddleaddrgen_4_2_7_9159cb8bcee7fcb95582f140960cdae72788d326 twag (
    .clk(clk),
    .phase(ph2),
    .bitpermout(bitpermout),
    .twaddr(twag_twaddr),
    .bitpermin(twag_bitpermin));
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:83:9  */
  complexmultiply2_11_8_8_bf8b4530d8d246dd74ac53a13471bba17941dff7 twmult (
    .clk(clk),
    .in1_re(n738_o),
    .in1_im(n739_o),
    .in2_re(n740_o),
    .in2_im(n741_o),
    .out1_re(twmult_out1_re),
    .out1_im(twmult_out1_im));
  assign n738_o = twdata[47:0];
  assign n739_o = twdata[95:48];
  assign n740_o = transpout[47:0];
  assign n741_o = transpout[95:48];
  assign n742_o = {twmult_out1_im, twmult_out1_re};
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:89:19  */
  assign n745_o = ph2 - 6'b000101;
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:89:21  */
  assign n747_o = n745_o + 6'b000001;
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:90:25  */
  assign n750_o = ph3[1:0];
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:92:32  */
  assign n751_o = bitpermin[0];
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:92:45  */
  assign n752_o = bitpermin[1];
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:92:35  */
  assign n753_o = {n751_o, n752_o};
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:92:58  */
  assign n754_o = bitpermin[2];
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:92:48  */
  assign n755_o = {n753_o, n754_o};
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:92:71  */
  assign n756_o = bitpermin[3];
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:92:61  */
  assign n757_o = {n755_o, n756_o};
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:94:9  */
  twiddlegenerator_10_6_2_3f29546453678b855931c174a97d6c0894b8f546 tw (
    .clk(clk),
    .rdaddr(twaddr),
    .romdata(romdata),
    .rddata_re(tw_rddata_re),
    .rddata_im(tw_rddata_im),
    .romaddr(tw_romaddr));
  assign n758_o = {tw_rddata_im, tw_rddata_re};
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:98:9  */
  twiddlerom64_10 rom (
    .clk(clk),
    .romaddr(romaddr),
    .romdata(rom_romdata));
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:100:9  */
  fft4096_sub16_2_8_10_bf8b4530d8d246dd74ac53a13471bba17941dff7 sub1 (
    .clk(clk),
    .din_re(n762_o),
    .din_im(n763_o),
    .phase(sub1phase),
    .dout_re(sub1_dout_re),
    .dout_im(sub1_dout_im));
  assign n762_o = sub1din[47:0];
  assign n763_o = sub1din[95:48];
  assign n764_o = {sub1_dout_im, sub1_dout_re};
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:102:9  */
  fft4_serial8_8_0_0_0201fbb6ff0978da8799292b5725f3cbccd5acf0 sub2inst (
    .clk(clk),
    .din_re(n766_o),
    .din_im(n767_o),
    .phase(sub2phase),
    .dout_re(sub2inst_dout_re),
    .dout_im(sub2inst_dout_im));
  assign n766_o = sub2din[47:0];
  assign n767_o = sub2din[95:48];
  assign n768_o = {sub2inst_dout_im, sub2inst_dout_re};
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:61:27  */
  always @(posedge clk)
    n770_q <= n728_o;
  /* ../fpga-fft/generated/fft4096/fft4096_sub64_2.vhd:89:24  */
  always @(posedge clk)
    n771_q <= n747_o;
endmodule

module fft4096_sub64_8_10_bf8b4530d8d246dd74ac53a13471bba17941dff7
  (input  clk,
   input  [47:0] din_re,
   input  [47:0] din_im,
   input  [5:0] phase,
   output [47:0] dout_re,
   output [47:0] dout_im);
  wire [95:0] n667_o;
  wire [47:0] n669_o;
  wire [47:0] n670_o;
  wire [95:0] sub1din;
  wire [95:0] sub1dout;
  wire [95:0] sub2din;
  wire [95:0] sub2dout;
  wire [3:0] sub1phase;
  wire [1:0] sub2phase;
  wire [5:0] ph1;
  wire [5:0] ph2;
  wire [5:0] ph3;
  wire [95:0] transpout;
  wire [3:0] bitpermin;
  wire [3:0] bitpermout;
  wire [5:0] twaddr;
  wire [95:0] twdata;
  wire [2:0] romaddr;
  wire [17:0] romdata;
  wire [3:0] n671_o;
  wire [5:0] n673_o;
  wire [5:0] n675_o;
  wire [47:0] transp_dout_re;
  wire [47:0] transp_dout_im;
  wire [47:0] n678_o;
  wire [47:0] n679_o;
  wire [95:0] n680_o;
  localparam n682_o = 1'b1;
  wire [5:0] twag_twaddr;
  wire [3:0] twag_bitpermin;
  wire [47:0] twmult_out1_re;
  wire [47:0] twmult_out1_im;
  wire [47:0] n685_o;
  wire [47:0] n686_o;
  wire [47:0] n687_o;
  wire [47:0] n688_o;
  wire [95:0] n689_o;
  wire [5:0] n692_o;
  wire [5:0] n694_o;
  wire [1:0] n697_o;
  wire n698_o;
  wire n699_o;
  wire [1:0] n700_o;
  wire n701_o;
  wire [2:0] n702_o;
  wire n703_o;
  wire [3:0] n704_o;
  wire [47:0] tw_rddata_re;
  wire [47:0] tw_rddata_im;
  wire [2:0] tw_romaddr;
  wire [95:0] n705_o;
  wire [17:0] rom_romdata;
  wire [47:0] sub1_dout_re;
  wire [47:0] sub1_dout_im;
  wire [47:0] n709_o;
  wire [47:0] n710_o;
  wire [95:0] n711_o;
  wire [47:0] sub2inst_dout_re;
  wire [47:0] sub2inst_dout_im;
  wire [47:0] n713_o;
  wire [47:0] n714_o;
  wire [95:0] n715_o;
  reg [5:0] n717_q = 0;
  reg [5:0] n718_q = 0;
  assign dout_re = n669_o;
  assign dout_im = n670_o;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:74:51  */
  assign n667_o = {din_im, din_re};
  /* ../fpga-fft/rtl/reorder_buffer.vhd:37:17  */
  assign n669_o = sub2dout[47:0];
  /* ../fpga-fft/rtl/reorder_buffer.vhd:34:17  */
  assign n670_o = sub2dout[95:48];
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:30:16  */
  assign sub1din = n667_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:30:25  */
  assign sub1dout = n711_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:30:35  */
  assign sub2din = n689_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:30:44  */
  assign sub2dout = n715_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:31:16  */
  assign sub1phase = n671_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:32:16  */
  assign sub2phase = n697_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:46:16  */
  assign ph1 = n717_q; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:46:21  */
  assign ph2 = ph1; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:46:26  */
  assign ph3 = n718_q; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:47:22  */
  assign transpout = n680_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:48:16  */
  assign bitpermin = twag_bitpermin; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:48:26  */
  assign bitpermout = n704_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:51:16  */
  assign twaddr = twag_twaddr; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:52:16  */
  assign twdata = n705_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:54:16  */
  assign romaddr = tw_romaddr; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:55:16  */
  assign romdata = rom_romdata; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:59:27  */
  assign n671_o = phase[3:0];
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:61:21  */
  assign n673_o = phase - 6'b100011;
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:61:24  */
  assign n675_o = n673_o + 6'b000001;
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:63:9  */
  transposer_2_4_8 transp (
    .clk(clk),
    .din_re(n678_o),
    .din_im(n679_o),
    .phase(ph1),
    .reorderenable(n682_o),
    .dout_re(transp_dout_re),
    .dout_im(transp_dout_im));
  assign n678_o = sub1dout[47:0];
  assign n679_o = sub1dout[95:48];
  assign n680_o = {transp_dout_im, transp_dout_re};
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:69:9  */
  twiddleaddrgen_4_2_7_9159cb8bcee7fcb95582f140960cdae72788d326 twag (
    .clk(clk),
    .phase(ph2),
    .bitpermout(bitpermout),
    .twaddr(twag_twaddr),
    .bitpermin(twag_bitpermin));
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:83:9  */
  complexmultiply2_11_8_8_bf8b4530d8d246dd74ac53a13471bba17941dff7 twmult (
    .clk(clk),
    .in1_re(n685_o),
    .in1_im(n686_o),
    .in2_re(n687_o),
    .in2_im(n688_o),
    .out1_re(twmult_out1_re),
    .out1_im(twmult_out1_im));
  assign n685_o = twdata[47:0];
  assign n686_o = twdata[95:48];
  assign n687_o = transpout[47:0];
  assign n688_o = transpout[95:48];
  assign n689_o = {twmult_out1_im, twmult_out1_re};
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:89:19  */
  assign n692_o = ph2 - 6'b000101;
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:89:21  */
  assign n694_o = n692_o + 6'b000001;
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:90:25  */
  assign n697_o = ph3[1:0];
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:92:32  */
  assign n698_o = bitpermin[0];
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:92:45  */
  assign n699_o = bitpermin[1];
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:92:35  */
  assign n700_o = {n698_o, n699_o};
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:92:58  */
  assign n701_o = bitpermin[2];
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:92:48  */
  assign n702_o = {n700_o, n701_o};
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:92:71  */
  assign n703_o = bitpermin[3];
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:92:61  */
  assign n704_o = {n702_o, n703_o};
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:94:9  */
  twiddlegenerator_10_6_2_3f29546453678b855931c174a97d6c0894b8f546 tw (
    .clk(clk),
    .rdaddr(twaddr),
    .romdata(romdata),
    .rddata_re(tw_rddata_re),
    .rddata_im(tw_rddata_im),
    .romaddr(tw_romaddr));
  assign n705_o = {tw_rddata_im, tw_rddata_re};
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:98:9  */
  twiddlerom64_10 rom (
    .clk(clk),
    .romaddr(romaddr),
    .romdata(rom_romdata));
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:100:9  */
  fft4096_sub16_8_10_bf8b4530d8d246dd74ac53a13471bba17941dff7 sub1 (
    .clk(clk),
    .din_re(n709_o),
    .din_im(n710_o),
    .phase(sub1phase),
    .dout_re(sub1_dout_re),
    .dout_im(sub1_dout_im));
  assign n709_o = sub1din[47:0];
  assign n710_o = sub1din[95:48];
  assign n711_o = {sub1_dout_im, sub1_dout_re};
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:102:9  */
  fft4_serial8_8_0_2_0201fbb6ff0978da8799292b5725f3cbccd5acf0 sub2inst (
    .clk(clk),
    .din_re(n713_o),
    .din_im(n714_o),
    .phase(sub2phase),
    .dout_re(sub2inst_dout_re),
    .dout_im(sub2inst_dout_im));
  assign n713_o = sub2din[47:0];
  assign n714_o = sub2din[95:48];
  assign n715_o = {sub2inst_dout_im, sub2inst_dout_re};
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:61:27  */
  always @(posedge clk)
    n717_q <= n675_o;
  /* ../fpga-fft/generated/fft4096/fft4096_sub64.vhd:89:24  */
  always @(posedge clk)
    n718_q <= n694_o;
endmodule

module reorderbuffer_6_8_2_0_0
  (input  clk,
   input  [47:0] din_re,
   input  [47:0] din_im,
   input  [5:0] phase,
   input  [5:0] bitpermout,
   output [47:0] dout_re,
   output [47:0] dout_im,
   output [5:0] bitpermin,
   output bitpermcount);
  wire [95:0] n619_o;
  wire [47:0] n621_o;
  wire [47:0] n622_o;
  wire [95:0] din2;
  wire [95:0] dout0;
  wire [5:0] iaddr;
  wire [5:0] iaddr2;
  wire [5:0] oaddr;
  reg state = 0;
  reg statenext = 0;
  wire [5:0] ph1;
  wire [5:0] ph2;
  wire [5:0] n628_o;
  wire [5:0] n630_o;
  wire n637_o;
  wire n638_o;
  wire n640_o;
  wire n642_o;
  wire [47:0] g3_ram_rddata_re;
  wire [47:0] g3_ram_rddata_im;
  wire [95:0] n648_o;
  localparam n650_o = 1'b1;
  wire [47:0] n651_o;
  wire [47:0] n652_o;
  wire [5:0] sr1_dout;
  localparam n654_o = 1'b1;
  reg [95:0] n659_q = 0;
  reg [5:0] n660_q = 0;
  reg [5:0] n661_q = 0;
  wire n662_o;
  reg n663_q = 0;
  reg [5:0] n664_q = 0;
  reg [5:0] n665_q = 0;
  assign dout_re = n621_o;
  assign dout_im = n622_o;
  assign bitpermin = ph2;
  assign bitpermcount = state;
  /* ../fpga-fft/generated/fft4096/twiddle_rom_4096.vhd:31:22  */
  assign n619_o = {din_im, din_re};
  assign n621_o = dout0[47:0];
  /* ../fpga-fft/rtl/fft_types.vhd:49:14  */
  assign n622_o = dout0[95:48];
  /* ../fpga-fft/rtl/reorder_buffer.vhd:43:16  */
  assign din2 = n659_q; // (signal)
  /* ../fpga-fft/rtl/reorder_buffer.vhd:43:21  */
  assign dout0 = n648_o; // (signal)
  /* ../fpga-fft/rtl/reorder_buffer.vhd:44:16  */
  assign iaddr = sr1_dout; // (signal)
  /* ../fpga-fft/rtl/reorder_buffer.vhd:44:23  */
  assign iaddr2 = n660_q; // (signal)
  /* ../fpga-fft/rtl/reorder_buffer.vhd:44:31  */
  assign oaddr = n661_q; // (signal)
  /* ../fpga-fft/rtl/reorder_buffer.vhd:53:16  */
  always @*
    state = n663_q; // (isignal)
  initial
    state = 1'b0;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:53:22  */
  always @*
    statenext = n638_o; // (isignal)
  initial
    statenext = 1'b0;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:54:16  */
  assign ph1 = n664_q; // (signal)
  /* ../fpga-fft/rtl/reorder_buffer.vhd:54:20  */
  assign ph2 = n665_q; // (signal)
  /* ../fpga-fft/rtl/reorder_buffer.vhd:57:21  */
  assign n628_o = phase + 6'b000101;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:57:33  */
  assign n630_o = n628_o - 6'b000000;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:61:46  */
  assign n637_o = $unsigned(state) >= $unsigned(1'b1);
  /* ../fpga-fft/rtl/reorder_buffer.vhd:61:36  */
  assign n638_o = n637_o ? 1'b0 : n640_o;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:61:71  */
  assign n640_o = state + 1'b1;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:62:36  */
  assign n642_o = ph1 == 6'b000000;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:73:17  */
  complexramlut_8_6 g3_ram (
    .rdclk(clk),
    .wrclk(clk),
    .rdaddr(oaddr),
    .wren(n650_o),
    .wraddr(iaddr2),
    .wrdata_re(n651_o),
    .wrdata_im(n652_o),
    .rddata_re(g3_ram_rddata_re),
    .rddata_im(g3_ram_rddata_im));
  /* ../fpga-fft/rtl/fft_types.vhd:49:14  */
  assign n648_o = {g3_ram_rddata_im, g3_ram_rddata_re};
  /* ../fpga-fft/rtl/fft_types.vhd:49:14  */
  assign n651_o = din2[47:0];
  assign n652_o = din2[95:48];
  /* ../fpga-fft/rtl/reorder_buffer.vhd:96:9  */
  sr_unsigned_6_2 sr1 (
    .clk(clk),
    .din(oaddr),
    .ce(n654_o),
    .dout(sr1_dout));
  /* ../fpga-fft/rtl/reorder_buffer.vhd:98:21  */
  always @(posedge clk)
    n659_q <= n619_o;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:99:25  */
  always @(posedge clk)
    n660_q <= iaddr;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:67:29  */
  always @(posedge clk)
    n661_q <= bitpermout;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:62:28  */
  assign n662_o = n642_o ? statenext : state;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:62:28  */
  always @(posedge clk)
    n663_q <= n662_o;
  initial
    n663_q = 1'b0;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:57:48  */
  always @(posedge clk)
    n664_q <= n630_o;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:60:20  */
  always @(posedge clk)
    n665_q <= ph1;
endmodule

module twiddlerom4096_10
  (input  clk,
   input  [8:0] romaddr,
   output [17:0] romdata);
  wire [9215:0] rom;
  wire [8:0] addr1;
  wire [17:0] data0;
  wire [17:0] data1;
  wire [8:0] n609_o;
  reg [8:0] n615_q = 0;
  reg [17:0] n616_q = 0;
  wire [17:0] n618_data; // mem_rd
  assign romdata = data1;
  /* ../fpga-fft/generated/fft4096/twiddle_rom_4096.vhd:22:16  */
  assign rom = 9216'b000000001111111111000000010111111111000000010111111111000000011111111111000000100111111111000000101111111111000000101111111111000000110111111111000000111111111111000001000111111111000001001111111111000001001111111111000001010111111111000001011111111111000001100111111111000001101111111111000001101111111111000001110111111111000001111111111111000010000111111111000010000111111111000010001111111111000010010111111111000010011111111111000010100111111111000010100111111111000010101111111111000010110111111111000010111111111111000011000111111111000011000111111111000011001111111111000011010111111111000011011111111111000011011111111111000011100111111111000011101111111111000011110111111111000011111111111111000011111111111111000100000111111111000100001111111111000100010111111111000100011111111111000100011111111111000100100111111111000100101111111111000100110111111111000100110111111111000100111111111110000101000111111110000101001111111110000101010111111110000101010111111110000101011111111110000101100111111110000101101111111110000101101111111110000101110111111110000101111111111110000110000111111110000110001111111110000110001111111110000110010111111110000110011111111101000110100111111101000110101111111101000110101111111101000110110111111101000110111111111101000111000111111101000111000111111101000111001111111101000111010111111101000111011111111101000111100111111101000111100111111100000111101111111100000111110111111100000111111111111100000111111111111100001000000111111100001000001111111100001000010111111100001000011111111100001000011111111100001000100111111011001000101111111011001000110111111011001000110111111011001000111111111011001001000111111011001001001111111011001001010111111011001001010111111011001001011111111010001001100111111010001001101111111010001001101111111010001001110111111010001001111111111010001010000111111010001010001111111010001010001111111001001010010111111001001010011111111001001010100111111001001010100111111001001010101111111001001010110111111001001010111111111001001011000111111000001011000111111000001011001111111000001011010111111000001011011111111000001011011111111000001011100111111000001011101111110111001011110111110111001011110111110111001011111111110111001100000111110111001100001111110111001100010111110111001100010111110110001100011111110110001100100111110110001100101111110110001100101111110110001100110111110110001100111111110110001101000111110101001101001111110101001101001111110101001101010111110101001101011111110101001101100111110101001101100111110100001101101111110100001101110111110100001101111111110100001101111111110100001110000111110100001110001111110011001110010111110011001110010111110011001110011111110011001110100111110011001110101111110011001110110111110010001110110111110010001110111111110010001111000111110010001111001111110010001111001111110001001111010111110001001111011111110001001111100111110001001111100111110001001111101111110000001111110111110000001111111111110000001111111111110000010000000111110000010000001111101111010000010111101111010000010111101111010000011111101111010000100111101111010000101111101110010000110111101110010000110111101110010000111111101110010001000111101110010001001111101101010001001111101101010001010111101101010001011111101101010001100111101101010001100111101100010001101111101100010001110111101100010001111111101100010001111111101100010010000111101011010010001111101011010010010111101011010010010111101011010010011111101010010010100111101010010010101111101010010010101111101010010010110111101001010010111111101001010011000111101001010011000111101001010011001111101001010011010111101000010011011111101000010011011111101000010011100111101000010011101111100111010011110111100111010011110111100111010011111111100111010100000111100110010100001111100110010100001111100110010100010111100110010100011111100101010100100111100101010100100111100101010100101111100101010100110111100100010100111111100100010100111111100100010101000111100100010101001111100011010101010111100011010101010111100011010101011111100011010101100111100010010101100111100010010101101111100010010101110111100010010101111111100001010101111111100001010110000111100001010110001111100000010110010111100000010110010111100000010110011111100000010110100111011111010110101111011111010110101111011111010110110111011111010110111111011110010111000111011110010111000111011110010111001111011101010111010111011101010111010111011101010111011111011101010111100111011100010111101111011100010111101111011100010111110111011011010111111111011011011000000111011011011000000111011011011000001111011010011000010111011010011000010111011010011000011111011001011000100111011001011000101111011001011000101111011000011000110111011000011000111111011000011001000111011000011001000111010111011001001111010111011001010111010111011001010111010110011001011111010110011001100111010110011001101111010101011001101111010101011001110111010101011001111111010100011001111111010100011010000111010100011010001111010011011010010111010011011010010111010011011010011111010010011010100111010010011010100111010010011010101111010001011010110111010001011010111111010001011010111111010001011011000111010000011011001111010000011011001111010000011011010111001111011011011111001111011011100111001111011011100111001110011011101111001110011011110111001101011011110111001101011011111111001101011100000111001100011100001111001100011100001111001100011100010111001011011100011111001011011100011111001011011100100111001010011100101111001010011100101111001010011100110111001001011100111111001001011101000111001001011101000111001000011101001111001000011101010111001000011101010111000111011101011111000111011101100111000110011101100111000110011101101111000110011101110111000101011101111111000101011101111111000101011110000111000100011110001111000100011110001111000100011110010111000011011110011111000011011110011111000010011110100111000010011110101111000010011110110111000001011110110111000001011110111111000001011111000111000000011111000111000000011111001110111111011111010110111111011111010110111111011111011110111110011111100110111110011111100110111101011111101110111101011111110110111101011111110110111100011111111110111100100000000110111100100000000110111011100000001110111011100000010110111010100000010110111010100000011110111010100000100110111001100000101110111001100000101110111000100000110110111000100000111110111000100000111110110111100001000110110111100001001110110110100001001110110110100001010110110110100001011110110101100001011110110101100001100110110100100001101110110100100001101110110011100001110110110011100001111110110011100001111110110010100010000110110010100010001110110001100010001110110001100010010110110001100010011110110000100010011110110000100010100110101111100010101110101111100010101110101110100010110110101110100010111110101110100010111110101101100011000110101101100011001110101100100011001110101100100011010110101011100011010110101011100011011110101011100011100110101010100011100110101010100011101110101001100011110110101001100011110110101000100011111110101000100100000110101000100100000110100111100100001110100111100100010110100110100100010110100110100100011110100101100100100110100101100100100110100100100100101110100100100100110110100100100100110110100011100100111110100011100100111110100010100101000110100010100101001110100001100101001110100001100101010110100000100101011110100000100101011110011111100101100110011111100101101110011110100101101110011110100101110110011110100101110110011101100101111110011101100110000110011100100110000110011100100110001110011011100110010110011011100110010110011010100110011110011010100110100110011001100110100110011001100110101110011000100110101110011000100110110110010111100110111110010111100110111110010111100111000110010110100111001110010110100111001110010101100111010110010101100111010110010100100111011110010100100111100110010011100111100110010011100111101110010010100111101110010010100111110110010001100111111110010001100111111110010000101000000110010000101000001110001111101000001110001111101000010110001110101000010110001110101000011110001101101000100110001101101000100110001100101000101110001100101000101110001011101000110110001011101000111110001010101000111110001010101001000110001001101001000110001001101001001110001000101001010110001000101001010110000111101001011110000111101001011110000110101001100110000110101001101110000101101001101110000101101001110110000100101001110110000100101001111110000011101010000110000011101010000110000010101010001110000010101010001110000001101010010110000001101010011110000000101010011110000000101010100101111111101010100101111111101010101101111110101010110101111101101010110101111101101010111101111100101010111101111100101011000101111011101011000101111011101011001101111010101011010101111010101011010101111001101011011101111001101011011101111000101011100101111000101011100101110111101011101101110111101011110101110110101011110101110110101011111101110101101011111101110100101100000101110100101100000101110011101100001101110011101100010101110010101100010101110010101100011101110001101100011101110001101100100101110000101100100101110000101100101101101111101100110101101110101100110101101110101100111101101101101100111101101101101101000101101100101101000101101100101101001101101011101101001101101011101101010101101010; // (signal)
  /* ../fpga-fft/generated/fft4096/twiddle_rom_4096.vhd:23:16  */
  assign addr1 = n615_q; // (signal)
  /* ../fpga-fft/generated/fft4096/twiddle_rom_4096.vhd:24:16  */
  assign data0 = n618_data; // (signal)
  /* ../fpga-fft/generated/fft4096/twiddle_rom_4096.vhd:24:22  */
  assign data1 = n616_q; // (signal)
  /* ../fpga-fft/generated/fft4096/twiddle_rom_4096.vhd:31:22  */
  assign n609_o = 9'b111111111 - addr1;
  /* ../fpga-fft/generated/fft4096/twiddle_rom_4096.vhd:30:26  */
  always @(posedge clk)
    n615_q <= romaddr;
  /* ../fpga-fft/generated/fft4096/twiddle_rom_4096.vhd:32:24  */
  always @(posedge clk)
    n616_q <= data0;
  /* ../fpga-fft/generated/fft4096/twiddle_rom_4096.vhd:12:25  */
  reg [17:0] n617[511:0] ; // memor = 0;
  initial begin
    n617[511] = 18'b000000001111111111;
    n617[510] = 18'b000000010111111111;
    n617[509] = 18'b000000010111111111;
    n617[508] = 18'b000000011111111111;
    n617[507] = 18'b000000100111111111;
    n617[506] = 18'b000000101111111111;
    n617[505] = 18'b000000101111111111;
    n617[504] = 18'b000000110111111111;
    n617[503] = 18'b000000111111111111;
    n617[502] = 18'b000001000111111111;
    n617[501] = 18'b000001001111111111;
    n617[500] = 18'b000001001111111111;
    n617[499] = 18'b000001010111111111;
    n617[498] = 18'b000001011111111111;
    n617[497] = 18'b000001100111111111;
    n617[496] = 18'b000001101111111111;
    n617[495] = 18'b000001101111111111;
    n617[494] = 18'b000001110111111111;
    n617[493] = 18'b000001111111111111;
    n617[492] = 18'b000010000111111111;
    n617[491] = 18'b000010000111111111;
    n617[490] = 18'b000010001111111111;
    n617[489] = 18'b000010010111111111;
    n617[488] = 18'b000010011111111111;
    n617[487] = 18'b000010100111111111;
    n617[486] = 18'b000010100111111111;
    n617[485] = 18'b000010101111111111;
    n617[484] = 18'b000010110111111111;
    n617[483] = 18'b000010111111111111;
    n617[482] = 18'b000011000111111111;
    n617[481] = 18'b000011000111111111;
    n617[480] = 18'b000011001111111111;
    n617[479] = 18'b000011010111111111;
    n617[478] = 18'b000011011111111111;
    n617[477] = 18'b000011011111111111;
    n617[476] = 18'b000011100111111111;
    n617[475] = 18'b000011101111111111;
    n617[474] = 18'b000011110111111111;
    n617[473] = 18'b000011111111111111;
    n617[472] = 18'b000011111111111111;
    n617[471] = 18'b000100000111111111;
    n617[470] = 18'b000100001111111111;
    n617[469] = 18'b000100010111111111;
    n617[468] = 18'b000100011111111111;
    n617[467] = 18'b000100011111111111;
    n617[466] = 18'b000100100111111111;
    n617[465] = 18'b000100101111111111;
    n617[464] = 18'b000100110111111111;
    n617[463] = 18'b000100110111111111;
    n617[462] = 18'b000100111111111110;
    n617[461] = 18'b000101000111111110;
    n617[460] = 18'b000101001111111110;
    n617[459] = 18'b000101010111111110;
    n617[458] = 18'b000101010111111110;
    n617[457] = 18'b000101011111111110;
    n617[456] = 18'b000101100111111110;
    n617[455] = 18'b000101101111111110;
    n617[454] = 18'b000101101111111110;
    n617[453] = 18'b000101110111111110;
    n617[452] = 18'b000101111111111110;
    n617[451] = 18'b000110000111111110;
    n617[450] = 18'b000110001111111110;
    n617[449] = 18'b000110001111111110;
    n617[448] = 18'b000110010111111110;
    n617[447] = 18'b000110011111111101;
    n617[446] = 18'b000110100111111101;
    n617[445] = 18'b000110101111111101;
    n617[444] = 18'b000110101111111101;
    n617[443] = 18'b000110110111111101;
    n617[442] = 18'b000110111111111101;
    n617[441] = 18'b000111000111111101;
    n617[440] = 18'b000111000111111101;
    n617[439] = 18'b000111001111111101;
    n617[438] = 18'b000111010111111101;
    n617[437] = 18'b000111011111111101;
    n617[436] = 18'b000111100111111101;
    n617[435] = 18'b000111100111111100;
    n617[434] = 18'b000111101111111100;
    n617[433] = 18'b000111110111111100;
    n617[432] = 18'b000111111111111100;
    n617[431] = 18'b000111111111111100;
    n617[430] = 18'b001000000111111100;
    n617[429] = 18'b001000001111111100;
    n617[428] = 18'b001000010111111100;
    n617[427] = 18'b001000011111111100;
    n617[426] = 18'b001000011111111100;
    n617[425] = 18'b001000100111111011;
    n617[424] = 18'b001000101111111011;
    n617[423] = 18'b001000110111111011;
    n617[422] = 18'b001000110111111011;
    n617[421] = 18'b001000111111111011;
    n617[420] = 18'b001001000111111011;
    n617[419] = 18'b001001001111111011;
    n617[418] = 18'b001001010111111011;
    n617[417] = 18'b001001010111111011;
    n617[416] = 18'b001001011111111010;
    n617[415] = 18'b001001100111111010;
    n617[414] = 18'b001001101111111010;
    n617[413] = 18'b001001101111111010;
    n617[412] = 18'b001001110111111010;
    n617[411] = 18'b001001111111111010;
    n617[410] = 18'b001010000111111010;
    n617[409] = 18'b001010001111111010;
    n617[408] = 18'b001010001111111001;
    n617[407] = 18'b001010010111111001;
    n617[406] = 18'b001010011111111001;
    n617[405] = 18'b001010100111111001;
    n617[404] = 18'b001010100111111001;
    n617[403] = 18'b001010101111111001;
    n617[402] = 18'b001010110111111001;
    n617[401] = 18'b001010111111111001;
    n617[400] = 18'b001011000111111000;
    n617[399] = 18'b001011000111111000;
    n617[398] = 18'b001011001111111000;
    n617[397] = 18'b001011010111111000;
    n617[396] = 18'b001011011111111000;
    n617[395] = 18'b001011011111111000;
    n617[394] = 18'b001011100111111000;
    n617[393] = 18'b001011101111110111;
    n617[392] = 18'b001011110111110111;
    n617[391] = 18'b001011110111110111;
    n617[390] = 18'b001011111111110111;
    n617[389] = 18'b001100000111110111;
    n617[388] = 18'b001100001111110111;
    n617[387] = 18'b001100010111110111;
    n617[386] = 18'b001100010111110110;
    n617[385] = 18'b001100011111110110;
    n617[384] = 18'b001100100111110110;
    n617[383] = 18'b001100101111110110;
    n617[382] = 18'b001100101111110110;
    n617[381] = 18'b001100110111110110;
    n617[380] = 18'b001100111111110110;
    n617[379] = 18'b001101000111110101;
    n617[378] = 18'b001101001111110101;
    n617[377] = 18'b001101001111110101;
    n617[376] = 18'b001101010111110101;
    n617[375] = 18'b001101011111110101;
    n617[374] = 18'b001101100111110101;
    n617[373] = 18'b001101100111110100;
    n617[372] = 18'b001101101111110100;
    n617[371] = 18'b001101110111110100;
    n617[370] = 18'b001101111111110100;
    n617[369] = 18'b001101111111110100;
    n617[368] = 18'b001110000111110100;
    n617[367] = 18'b001110001111110011;
    n617[366] = 18'b001110010111110011;
    n617[365] = 18'b001110010111110011;
    n617[364] = 18'b001110011111110011;
    n617[363] = 18'b001110100111110011;
    n617[362] = 18'b001110101111110011;
    n617[361] = 18'b001110110111110010;
    n617[360] = 18'b001110110111110010;
    n617[359] = 18'b001110111111110010;
    n617[358] = 18'b001111000111110010;
    n617[357] = 18'b001111001111110010;
    n617[356] = 18'b001111001111110001;
    n617[355] = 18'b001111010111110001;
    n617[354] = 18'b001111011111110001;
    n617[353] = 18'b001111100111110001;
    n617[352] = 18'b001111100111110001;
    n617[351] = 18'b001111101111110000;
    n617[350] = 18'b001111110111110000;
    n617[349] = 18'b001111111111110000;
    n617[348] = 18'b001111111111110000;
    n617[347] = 18'b010000000111110000;
    n617[346] = 18'b010000001111101111;
    n617[345] = 18'b010000010111101111;
    n617[344] = 18'b010000010111101111;
    n617[343] = 18'b010000011111101111;
    n617[342] = 18'b010000100111101111;
    n617[341] = 18'b010000101111101110;
    n617[340] = 18'b010000110111101110;
    n617[339] = 18'b010000110111101110;
    n617[338] = 18'b010000111111101110;
    n617[337] = 18'b010001000111101110;
    n617[336] = 18'b010001001111101101;
    n617[335] = 18'b010001001111101101;
    n617[334] = 18'b010001010111101101;
    n617[333] = 18'b010001011111101101;
    n617[332] = 18'b010001100111101101;
    n617[331] = 18'b010001100111101100;
    n617[330] = 18'b010001101111101100;
    n617[329] = 18'b010001110111101100;
    n617[328] = 18'b010001111111101100;
    n617[327] = 18'b010001111111101100;
    n617[326] = 18'b010010000111101011;
    n617[325] = 18'b010010001111101011;
    n617[324] = 18'b010010010111101011;
    n617[323] = 18'b010010010111101011;
    n617[322] = 18'b010010011111101010;
    n617[321] = 18'b010010100111101010;
    n617[320] = 18'b010010101111101010;
    n617[319] = 18'b010010101111101010;
    n617[318] = 18'b010010110111101001;
    n617[317] = 18'b010010111111101001;
    n617[316] = 18'b010011000111101001;
    n617[315] = 18'b010011000111101001;
    n617[314] = 18'b010011001111101001;
    n617[313] = 18'b010011010111101000;
    n617[312] = 18'b010011011111101000;
    n617[311] = 18'b010011011111101000;
    n617[310] = 18'b010011100111101000;
    n617[309] = 18'b010011101111100111;
    n617[308] = 18'b010011110111100111;
    n617[307] = 18'b010011110111100111;
    n617[306] = 18'b010011111111100111;
    n617[305] = 18'b010100000111100110;
    n617[304] = 18'b010100001111100110;
    n617[303] = 18'b010100001111100110;
    n617[302] = 18'b010100010111100110;
    n617[301] = 18'b010100011111100101;
    n617[300] = 18'b010100100111100101;
    n617[299] = 18'b010100100111100101;
    n617[298] = 18'b010100101111100101;
    n617[297] = 18'b010100110111100100;
    n617[296] = 18'b010100111111100100;
    n617[295] = 18'b010100111111100100;
    n617[294] = 18'b010101000111100100;
    n617[293] = 18'b010101001111100011;
    n617[292] = 18'b010101010111100011;
    n617[291] = 18'b010101010111100011;
    n617[290] = 18'b010101011111100011;
    n617[289] = 18'b010101100111100010;
    n617[288] = 18'b010101100111100010;
    n617[287] = 18'b010101101111100010;
    n617[286] = 18'b010101110111100010;
    n617[285] = 18'b010101111111100001;
    n617[284] = 18'b010101111111100001;
    n617[283] = 18'b010110000111100001;
    n617[282] = 18'b010110001111100000;
    n617[281] = 18'b010110010111100000;
    n617[280] = 18'b010110010111100000;
    n617[279] = 18'b010110011111100000;
    n617[278] = 18'b010110100111011111;
    n617[277] = 18'b010110101111011111;
    n617[276] = 18'b010110101111011111;
    n617[275] = 18'b010110110111011111;
    n617[274] = 18'b010110111111011110;
    n617[273] = 18'b010111000111011110;
    n617[272] = 18'b010111000111011110;
    n617[271] = 18'b010111001111011101;
    n617[270] = 18'b010111010111011101;
    n617[269] = 18'b010111010111011101;
    n617[268] = 18'b010111011111011101;
    n617[267] = 18'b010111100111011100;
    n617[266] = 18'b010111101111011100;
    n617[265] = 18'b010111101111011100;
    n617[264] = 18'b010111110111011011;
    n617[263] = 18'b010111111111011011;
    n617[262] = 18'b011000000111011011;
    n617[261] = 18'b011000000111011011;
    n617[260] = 18'b011000001111011010;
    n617[259] = 18'b011000010111011010;
    n617[258] = 18'b011000010111011010;
    n617[257] = 18'b011000011111011001;
    n617[256] = 18'b011000100111011001;
    n617[255] = 18'b011000101111011001;
    n617[254] = 18'b011000101111011000;
    n617[253] = 18'b011000110111011000;
    n617[252] = 18'b011000111111011000;
    n617[251] = 18'b011001000111011000;
    n617[250] = 18'b011001000111010111;
    n617[249] = 18'b011001001111010111;
    n617[248] = 18'b011001010111010111;
    n617[247] = 18'b011001010111010110;
    n617[246] = 18'b011001011111010110;
    n617[245] = 18'b011001100111010110;
    n617[244] = 18'b011001101111010101;
    n617[243] = 18'b011001101111010101;
    n617[242] = 18'b011001110111010101;
    n617[241] = 18'b011001111111010100;
    n617[240] = 18'b011001111111010100;
    n617[239] = 18'b011010000111010100;
    n617[238] = 18'b011010001111010011;
    n617[237] = 18'b011010010111010011;
    n617[236] = 18'b011010010111010011;
    n617[235] = 18'b011010011111010010;
    n617[234] = 18'b011010100111010010;
    n617[233] = 18'b011010100111010010;
    n617[232] = 18'b011010101111010001;
    n617[231] = 18'b011010110111010001;
    n617[230] = 18'b011010111111010001;
    n617[229] = 18'b011010111111010001;
    n617[228] = 18'b011011000111010000;
    n617[227] = 18'b011011001111010000;
    n617[226] = 18'b011011001111010000;
    n617[225] = 18'b011011010111001111;
    n617[224] = 18'b011011011111001111;
    n617[223] = 18'b011011100111001111;
    n617[222] = 18'b011011100111001110;
    n617[221] = 18'b011011101111001110;
    n617[220] = 18'b011011110111001101;
    n617[219] = 18'b011011110111001101;
    n617[218] = 18'b011011111111001101;
    n617[217] = 18'b011100000111001100;
    n617[216] = 18'b011100001111001100;
    n617[215] = 18'b011100001111001100;
    n617[214] = 18'b011100010111001011;
    n617[213] = 18'b011100011111001011;
    n617[212] = 18'b011100011111001011;
    n617[211] = 18'b011100100111001010;
    n617[210] = 18'b011100101111001010;
    n617[209] = 18'b011100101111001010;
    n617[208] = 18'b011100110111001001;
    n617[207] = 18'b011100111111001001;
    n617[206] = 18'b011101000111001001;
    n617[205] = 18'b011101000111001000;
    n617[204] = 18'b011101001111001000;
    n617[203] = 18'b011101010111001000;
    n617[202] = 18'b011101010111000111;
    n617[201] = 18'b011101011111000111;
    n617[200] = 18'b011101100111000110;
    n617[199] = 18'b011101100111000110;
    n617[198] = 18'b011101101111000110;
    n617[197] = 18'b011101110111000101;
    n617[196] = 18'b011101111111000101;
    n617[195] = 18'b011101111111000101;
    n617[194] = 18'b011110000111000100;
    n617[193] = 18'b011110001111000100;
    n617[192] = 18'b011110001111000100;
    n617[191] = 18'b011110010111000011;
    n617[190] = 18'b011110011111000011;
    n617[189] = 18'b011110011111000010;
    n617[188] = 18'b011110100111000010;
    n617[187] = 18'b011110101111000010;
    n617[186] = 18'b011110110111000001;
    n617[185] = 18'b011110110111000001;
    n617[184] = 18'b011110111111000001;
    n617[183] = 18'b011111000111000000;
    n617[182] = 18'b011111000111000000;
    n617[181] = 18'b011111001110111111;
    n617[180] = 18'b011111010110111111;
    n617[179] = 18'b011111010110111111;
    n617[178] = 18'b011111011110111110;
    n617[177] = 18'b011111100110111110;
    n617[176] = 18'b011111100110111101;
    n617[175] = 18'b011111101110111101;
    n617[174] = 18'b011111110110111101;
    n617[173] = 18'b011111110110111100;
    n617[172] = 18'b011111111110111100;
    n617[171] = 18'b100000000110111100;
    n617[170] = 18'b100000000110111011;
    n617[169] = 18'b100000001110111011;
    n617[168] = 18'b100000010110111010;
    n617[167] = 18'b100000010110111010;
    n617[166] = 18'b100000011110111010;
    n617[165] = 18'b100000100110111001;
    n617[164] = 18'b100000101110111001;
    n617[163] = 18'b100000101110111000;
    n617[162] = 18'b100000110110111000;
    n617[161] = 18'b100000111110111000;
    n617[160] = 18'b100000111110110111;
    n617[159] = 18'b100001000110110111;
    n617[158] = 18'b100001001110110110;
    n617[157] = 18'b100001001110110110;
    n617[156] = 18'b100001010110110110;
    n617[155] = 18'b100001011110110101;
    n617[154] = 18'b100001011110110101;
    n617[153] = 18'b100001100110110100;
    n617[152] = 18'b100001101110110100;
    n617[151] = 18'b100001101110110011;
    n617[150] = 18'b100001110110110011;
    n617[149] = 18'b100001111110110011;
    n617[148] = 18'b100001111110110010;
    n617[147] = 18'b100010000110110010;
    n617[146] = 18'b100010001110110001;
    n617[145] = 18'b100010001110110001;
    n617[144] = 18'b100010010110110001;
    n617[143] = 18'b100010011110110000;
    n617[142] = 18'b100010011110110000;
    n617[141] = 18'b100010100110101111;
    n617[140] = 18'b100010101110101111;
    n617[139] = 18'b100010101110101110;
    n617[138] = 18'b100010110110101110;
    n617[137] = 18'b100010111110101110;
    n617[136] = 18'b100010111110101101;
    n617[135] = 18'b100011000110101101;
    n617[134] = 18'b100011001110101100;
    n617[133] = 18'b100011001110101100;
    n617[132] = 18'b100011010110101011;
    n617[131] = 18'b100011010110101011;
    n617[130] = 18'b100011011110101011;
    n617[129] = 18'b100011100110101010;
    n617[128] = 18'b100011100110101010;
    n617[127] = 18'b100011101110101001;
    n617[126] = 18'b100011110110101001;
    n617[125] = 18'b100011110110101000;
    n617[124] = 18'b100011111110101000;
    n617[123] = 18'b100100000110101000;
    n617[122] = 18'b100100000110100111;
    n617[121] = 18'b100100001110100111;
    n617[120] = 18'b100100010110100110;
    n617[119] = 18'b100100010110100110;
    n617[118] = 18'b100100011110100101;
    n617[117] = 18'b100100100110100101;
    n617[116] = 18'b100100100110100100;
    n617[115] = 18'b100100101110100100;
    n617[114] = 18'b100100110110100100;
    n617[113] = 18'b100100110110100011;
    n617[112] = 18'b100100111110100011;
    n617[111] = 18'b100100111110100010;
    n617[110] = 18'b100101000110100010;
    n617[109] = 18'b100101001110100001;
    n617[108] = 18'b100101001110100001;
    n617[107] = 18'b100101010110100000;
    n617[106] = 18'b100101011110100000;
    n617[105] = 18'b100101011110011111;
    n617[104] = 18'b100101100110011111;
    n617[103] = 18'b100101101110011110;
    n617[102] = 18'b100101101110011110;
    n617[101] = 18'b100101110110011110;
    n617[100] = 18'b100101110110011101;
    n617[99] = 18'b100101111110011101;
    n617[98] = 18'b100110000110011100;
    n617[97] = 18'b100110000110011100;
    n617[96] = 18'b100110001110011011;
    n617[95] = 18'b100110010110011011;
    n617[94] = 18'b100110010110011010;
    n617[93] = 18'b100110011110011010;
    n617[92] = 18'b100110100110011001;
    n617[91] = 18'b100110100110011001;
    n617[90] = 18'b100110101110011000;
    n617[89] = 18'b100110101110011000;
    n617[88] = 18'b100110110110010111;
    n617[87] = 18'b100110111110010111;
    n617[86] = 18'b100110111110010111;
    n617[85] = 18'b100111000110010110;
    n617[84] = 18'b100111001110010110;
    n617[83] = 18'b100111001110010101;
    n617[82] = 18'b100111010110010101;
    n617[81] = 18'b100111010110010100;
    n617[80] = 18'b100111011110010100;
    n617[79] = 18'b100111100110010011;
    n617[78] = 18'b100111100110010011;
    n617[77] = 18'b100111101110010010;
    n617[76] = 18'b100111101110010010;
    n617[75] = 18'b100111110110010001;
    n617[74] = 18'b100111111110010001;
    n617[73] = 18'b100111111110010000;
    n617[72] = 18'b101000000110010000;
    n617[71] = 18'b101000001110001111;
    n617[70] = 18'b101000001110001111;
    n617[69] = 18'b101000010110001110;
    n617[68] = 18'b101000010110001110;
    n617[67] = 18'b101000011110001101;
    n617[66] = 18'b101000100110001101;
    n617[65] = 18'b101000100110001100;
    n617[64] = 18'b101000101110001100;
    n617[63] = 18'b101000101110001011;
    n617[62] = 18'b101000110110001011;
    n617[61] = 18'b101000111110001010;
    n617[60] = 18'b101000111110001010;
    n617[59] = 18'b101001000110001001;
    n617[58] = 18'b101001000110001001;
    n617[57] = 18'b101001001110001000;
    n617[56] = 18'b101001010110001000;
    n617[55] = 18'b101001010110000111;
    n617[54] = 18'b101001011110000111;
    n617[53] = 18'b101001011110000110;
    n617[52] = 18'b101001100110000110;
    n617[51] = 18'b101001101110000101;
    n617[50] = 18'b101001101110000101;
    n617[49] = 18'b101001110110000100;
    n617[48] = 18'b101001110110000100;
    n617[47] = 18'b101001111110000011;
    n617[46] = 18'b101010000110000011;
    n617[45] = 18'b101010000110000010;
    n617[44] = 18'b101010001110000010;
    n617[43] = 18'b101010001110000001;
    n617[42] = 18'b101010010110000001;
    n617[41] = 18'b101010011110000000;
    n617[40] = 18'b101010011110000000;
    n617[39] = 18'b101010100101111111;
    n617[38] = 18'b101010100101111111;
    n617[37] = 18'b101010101101111110;
    n617[36] = 18'b101010110101111101;
    n617[35] = 18'b101010110101111101;
    n617[34] = 18'b101010111101111100;
    n617[33] = 18'b101010111101111100;
    n617[32] = 18'b101011000101111011;
    n617[31] = 18'b101011000101111011;
    n617[30] = 18'b101011001101111010;
    n617[29] = 18'b101011010101111010;
    n617[28] = 18'b101011010101111001;
    n617[27] = 18'b101011011101111001;
    n617[26] = 18'b101011011101111000;
    n617[25] = 18'b101011100101111000;
    n617[24] = 18'b101011100101110111;
    n617[23] = 18'b101011101101110111;
    n617[22] = 18'b101011110101110110;
    n617[21] = 18'b101011110101110110;
    n617[20] = 18'b101011111101110101;
    n617[19] = 18'b101011111101110100;
    n617[18] = 18'b101100000101110100;
    n617[17] = 18'b101100000101110011;
    n617[16] = 18'b101100001101110011;
    n617[15] = 18'b101100010101110010;
    n617[14] = 18'b101100010101110010;
    n617[13] = 18'b101100011101110001;
    n617[12] = 18'b101100011101110001;
    n617[11] = 18'b101100100101110000;
    n617[10] = 18'b101100100101110000;
    n617[9] = 18'b101100101101101111;
    n617[8] = 18'b101100110101101110;
    n617[7] = 18'b101100110101101110;
    n617[6] = 18'b101100111101101101;
    n617[5] = 18'b101100111101101101;
    n617[4] = 18'b101101000101101100;
    n617[3] = 18'b101101000101101100;
    n617[2] = 18'b101101001101101011;
    n617[1] = 18'b101101001101101011;
    n617[0] = 18'b101101010101101010;
    end
  assign n618_data = n617[n609_o];
  /* ../fpga-fft/generated/fft4096/twiddle_rom_4096.vhd:31:22  */
endmodule

module twiddlegenerator_10_12_2_3f29546453678b855931c174a97d6c0894b8f546
  (input  clk,
   input  [11:0] rdaddr,
   input  [17:0] romdata,
   output [47:0] rddata_re,
   output [47:0] rddata_im,
   output [8:0] romaddr);
  wire [47:0] n413_o;
  wire [47:0] n414_o;
  wire [17:0] romdata1;
  reg [8:0] romaddr0 = 0;
  reg [8:0] romaddrnext = 0;
  reg [11:0] phase = 0;
  reg [11:0] phase1 = 0;
  reg [11:0] phase2 = 0;
  reg [11:0] phase3 = 0;
  reg [2:0] ph3 = 0;
  reg [2:0] ph4 = 0;
  wire iszero;
  wire iszeronext;
  wire [31:0] re;
  wire [31:0] im;
  wire [31:0] re0;
  wire [31:0] im0;
  wire [31:0] re_p;
  wire [31:0] re_m;
  wire [31:0] im_p;
  wire [31:0] im_m;
  wire [95:0] outdata;
  wire [95:0] outdata0;
  wire [8:0] n424_o;
  wire [8:0] n426_o;
  wire n427_o;
  wire n428_o;
  wire [8:0] n429_o;
  wire [8:0] n430_o;
  wire [8:0] n431_o;
  wire [11:0] sr_dout;
  localparam n437_o = 1'b1;
  wire [9:0] n441_o;
  wire n443_o;
  wire n444_o;
  wire [31:0] n451_o;
  wire [8:0] n452_o;
  wire [30:0] n453_o;
  wire [31:0] n454_o;
  wire [31:0] n456_o;
  wire [8:0] n457_o;
  wire [30:0] n458_o;
  wire [31:0] n459_o;
  wire [2:0] n466_o;
  wire [31:0] n469_o;
  wire [31:0] n474_o;
  wire [47:0] n485_o;
  wire [47:0] n488_o;
  wire [95:0] n489_o;
  wire n491_o;
  wire [95:0] n492_o;
  wire [47:0] n499_o;
  wire [47:0] n502_o;
  wire [95:0] n503_o;
  wire n505_o;
  wire [95:0] n506_o;
  wire [47:0] n513_o;
  wire [47:0] n516_o;
  wire [95:0] n517_o;
  wire n519_o;
  wire [95:0] n520_o;
  wire [47:0] n527_o;
  wire [47:0] n530_o;
  wire [95:0] n531_o;
  wire n533_o;
  wire [95:0] n534_o;
  wire [47:0] n541_o;
  wire [47:0] n544_o;
  wire [95:0] n545_o;
  wire n547_o;
  wire [95:0] n548_o;
  wire [47:0] n555_o;
  wire [47:0] n558_o;
  wire [95:0] n559_o;
  wire n561_o;
  wire [95:0] n562_o;
  wire [47:0] n569_o;
  wire [47:0] n572_o;
  wire [95:0] n573_o;
  wire n575_o;
  wire [95:0] n576_o;
  wire [47:0] n583_o;
  wire [47:0] n586_o;
  wire [95:0] n587_o;
  reg [17:0] n590_q = 0;
  reg [8:0] n591_q = 0;
  reg [11:0] n592_q = 0;
  reg [11:0] n593_q = 0;
  reg [11:0] n594_q = 0;
  reg [2:0] n595_q = 0;
  reg n596_q = 0;
  reg [31:0] n597_q = 0;
  reg [31:0] n598_q = 0;
  reg [31:0] n599_q = 0;
  reg [31:0] n600_q = 0;
  reg [31:0] n601_q = 0;
  reg [31:0] n602_q = 0;
  reg [95:0] n603_q = 0;
  assign rddata_re = n413_o;
  assign rddata_im = n414_o;
  assign romaddr = romaddr0;
  /* ../fpga-fft/rtl/complex_multiply2.vhd:55:47  */
  assign n413_o = outdata[47:0];
  /* ../fpga-fft/rtl/complex_multiply2.vhd:52:47  */
  assign n414_o = outdata[95:48];
  /* ../fpga-fft/rtl/twiddle_generator.vhd:39:16  */
  assign romdata1 = n590_q; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:40:16  */
  always @*
    romaddr0 = n591_q; // (isignal)
  initial
    romaddr0 = 9'b000000000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:40:25  */
  always @*
    romaddrnext = n429_o; // (isignal)
  initial
    romaddrnext = 9'b000000000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:41:16  */
  always @*
    phase = n592_q; // (isignal)
  initial
    phase = 12'b000000000000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:41:22  */
  always @*
    phase1 = sr_dout; // (isignal)
  initial
    phase1 = 12'b000000000000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:41:29  */
  always @*
    phase2 = n593_q; // (isignal)
  initial
    phase2 = 12'b000000000000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:41:36  */
  always @*
    phase3 = n594_q; // (isignal)
  initial
    phase3 = 12'b000000000000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:42:16  */
  always @*
    ph3 = n466_o; // (isignal)
  initial
    ph3 = 3'b000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:42:20  */
  always @*
    ph4 = n595_q; // (isignal)
  initial
    ph4 = 3'b000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:43:16  */
  assign iszero = n596_q; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:43:23  */
  assign iszeronext = n444_o; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:45:16  */
  assign re = n597_q; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:45:19  */
  assign im = n598_q; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:45:22  */
  assign re0 = n451_o; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:45:26  */
  assign im0 = n456_o; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:45:31  */
  assign re_p = n599_q; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:45:37  */
  assign re_m = n600_q; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:45:43  */
  assign im_p = n601_q; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:45:49  */
  assign im_m = n602_q; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:46:16  */
  assign outdata = n603_q; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:46:25  */
  assign outdata0 = n492_o; // (signal)
  /* ../fpga-fft/rtl/twiddle_generator.vhd:51:30  */
  assign n424_o = rdaddr[8:0];
  /* ../fpga-fft/rtl/twiddle_generator.vhd:51:53  */
  assign n426_o = n424_o - 9'b000000001;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:51:67  */
  assign n427_o = rdaddr[9];
  /* ../fpga-fft/rtl/twiddle_generator.vhd:51:81  */
  assign n428_o = ~n427_o;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:51:56  */
  assign n429_o = n428_o ? n426_o : n431_o;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:52:49  */
  assign n430_o = rdaddr[8:0];
  /* ../fpga-fft/rtl/twiddle_generator.vhd:52:39  */
  assign n431_o = ~n430_o;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:60:9  */
  sr_unsigned_12_2 sr (
    .clk(clk),
    .din(phase),
    .ce(n437_o),
    .dout(sr_dout));
  /* ../fpga-fft/rtl/twiddle_generator.vhd:63:38  */
  assign n441_o = phase1[9:0];
  /* ../fpga-fft/rtl/twiddle_generator.vhd:63:61  */
  assign n443_o = n441_o == 10'b0000000000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:63:27  */
  assign n444_o = n443_o ? 1'b1 : 1'b0;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:68:20  */
  assign n451_o = iszero ? 32'b00000000000000000000001000000000 : n454_o;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:69:45  */
  assign n452_o = romdata1[8:0];
  /* ../fpga-fft/rtl/twiddle_generator.vhd:69:17  */
  assign n453_o = {22'b0, n452_o};  //  uext
  /* ../fpga-fft/rtl/twiddle_generator.vhd:69:17  */
  assign n454_o = {1'b0, n453_o};  //  uext
  /* ../fpga-fft/rtl/twiddle_generator.vhd:70:18  */
  assign n456_o = iszero ? 32'b00000000000000000000000000000000 : n459_o;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:71:45  */
  assign n457_o = romdata1[17:9];
  /* ../fpga-fft/rtl/twiddle_generator.vhd:71:17  */
  assign n458_o = {22'b0, n457_o};  //  uext
  /* ../fpga-fft/rtl/twiddle_generator.vhd:71:17  */
  assign n459_o = {1'b0, n458_o};  //  uext
  /* ../fpga-fft/rtl/twiddle_generator.vhd:75:22  */
  assign n466_o = phase3[11:9];
  /* ../fpga-fft/rtl/twiddle_generator.vhd:79:17  */
  assign n469_o = -re;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:81:17  */
  assign n474_o = -im;
  /* ../fpga-fft/rtl/fft_types.vhd:131:27  */
  assign n485_o = {{16{re_p[31]}}, re_p}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:132:27  */
  assign n488_o = {{16{im_p[31]}}, im_p}; // sext
  assign n489_o = {n488_o, n485_o};
  /* ../fpga-fft/rtl/twiddle_generator.vhd:96:65  */
  assign n491_o = ph4 == 3'b000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:96:57  */
  assign n492_o = n491_o ? n489_o : n506_o;
  /* ../fpga-fft/rtl/fft_types.vhd:131:27  */
  assign n499_o = {{16{im_p[31]}}, im_p}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:132:27  */
  assign n502_o = {{16{re_p[31]}}, re_p}; // sext
  assign n503_o = {n502_o, n499_o};
  /* ../fpga-fft/rtl/twiddle_generator.vhd:97:73  */
  assign n505_o = ph4 == 3'b001;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:96:68  */
  assign n506_o = n505_o ? n503_o : n520_o;
  /* ../fpga-fft/rtl/fft_types.vhd:131:27  */
  assign n513_o = {{16{im_m[31]}}, im_m}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:132:27  */
  assign n516_o = {{16{re_p[31]}}, re_p}; // sext
  assign n517_o = {n516_o, n513_o};
  /* ../fpga-fft/rtl/twiddle_generator.vhd:98:73  */
  assign n519_o = ph4 == 3'b010;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:97:76  */
  assign n520_o = n519_o ? n517_o : n534_o;
  /* ../fpga-fft/rtl/fft_types.vhd:131:27  */
  assign n527_o = {{16{re_m[31]}}, re_m}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:132:27  */
  assign n530_o = {{16{im_p[31]}}, im_p}; // sext
  assign n531_o = {n530_o, n527_o};
  /* ../fpga-fft/rtl/twiddle_generator.vhd:99:73  */
  assign n533_o = ph4 == 3'b011;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:98:76  */
  assign n534_o = n533_o ? n531_o : n548_o;
  /* ../fpga-fft/rtl/fft_types.vhd:131:27  */
  assign n541_o = {{16{re_m[31]}}, re_m}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:132:27  */
  assign n544_o = {{16{im_m[31]}}, im_m}; // sext
  assign n545_o = {n544_o, n541_o};
  /* ../fpga-fft/rtl/twiddle_generator.vhd:100:73  */
  assign n547_o = ph4 == 3'b100;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:99:76  */
  assign n548_o = n547_o ? n545_o : n562_o;
  /* ../fpga-fft/rtl/fft_types.vhd:131:27  */
  assign n555_o = {{16{im_m[31]}}, im_m}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:132:27  */
  assign n558_o = {{16{re_m[31]}}, re_m}; // sext
  assign n559_o = {n558_o, n555_o};
  /* ../fpga-fft/rtl/twiddle_generator.vhd:101:73  */
  assign n561_o = ph4 == 3'b101;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:100:76  */
  assign n562_o = n561_o ? n559_o : n576_o;
  /* ../fpga-fft/rtl/fft_types.vhd:131:27  */
  assign n569_o = {{16{im_p[31]}}, im_p}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:132:27  */
  assign n572_o = {{16{re_m[31]}}, re_m}; // sext
  assign n573_o = {n572_o, n569_o};
  /* ../fpga-fft/rtl/twiddle_generator.vhd:102:73  */
  assign n575_o = ph4 == 3'b110;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:101:76  */
  assign n576_o = n575_o ? n573_o : n587_o;
  /* ../fpga-fft/rtl/fft_types.vhd:131:27  */
  assign n583_o = {{16{re_p[31]}}, re_p}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:132:27  */
  assign n586_o = {{16{im_m[31]}}, im_m}; // sext
  assign n587_o = {n586_o, n583_o};
  /* ../fpga-fft/rtl/twiddle_generator.vhd:65:29  */
  always @(posedge clk)
    n590_q <= romdata;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:53:33  */
  always @(posedge clk)
    n591_q <= romaddrnext;
  initial
    n591_q = 9'b000000000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:54:25  */
  always @(posedge clk)
    n592_q <= rdaddr;
  initial
    n592_q = 12'b000000000000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:62:26  */
  always @(posedge clk)
    n593_q <= phase1;
  initial
    n593_q = 12'b000000000000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:74:26  */
  always @(posedge clk)
    n594_q <= phase2;
  initial
    n594_q = 12'b000000000000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:82:20  */
  always @(posedge clk)
    n595_q <= ph3;
  initial
    n595_q = 3'b000;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:64:30  */
  always @(posedge clk)
    n596_q <= iszeronext;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:72:19  */
  always @(posedge clk)
    n597_q <= re0;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:73:19  */
  always @(posedge clk)
    n598_q <= im0;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:78:20  */
  always @(posedge clk)
    n599_q <= re;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:79:21  */
  always @(posedge clk)
    n600_q <= n469_o;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:80:20  */
  always @(posedge clk)
    n601_q <= im;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:81:21  */
  always @(posedge clk)
    n602_q <= n474_o;
  /* ../fpga-fft/rtl/twiddle_generator.vhd:106:29  */
  always @(posedge clk)
    n603_q <= outdata0;
endmodule

module complexmultiply2_11_8_8_bf8b4530d8d246dd74ac53a13471bba17941dff7
  (input  clk,
   input  [47:0] in1_re,
   input  [47:0] in1_im,
   input  [47:0] in2_re,
   input  [47:0] in2_im,
   output [47:0] out1_re,
   output [47:0] out1_im);
  wire [95:0] n306_o;
  wire [95:0] n307_o;
  wire [47:0] n309_o;
  wire [47:0] n310_o;
  wire [9:0] halflsb;
  wire [18:0] halflsb1;
  wire [10:0] a;
  wire [10:0] b;
  wire [10:0] b1;
  wire [7:0] c;
  wire [7:0] d;
  wire [7:0] c1;
  wire [7:0] d1;
  wire [18:0] ac3;
  wire [18:0] ad3;
  wire [18:0] bd4;
  wire [18:0] bc4;
  wire [7:0] res_re;
  wire [7:0] res_im;
  wire [10:0] n316_o;
  wire [10:0] n322_o;
  wire [7:0] n328_o;
  wire [7:0] n334_o;
  wire [18:0] n360_o;
  wire [18:0] madd1_p;
  wire [18:0] madd2_p;
  wire [18:0] madd3_p;
  wire [18:0] madd4_p;
  wire [7:0] n365_o;
  wire [7:0] n368_o;
  wire [47:0] n377_o;
  wire [47:0] n380_o;
  wire [95:0] n381_o;
  reg [10:0] n383_q = 0;
  reg [7:0] n388_q = 0;
  reg [7:0] n389_q = 0;
  reg [7:0] n410_q = 0;
  reg [7:0] n411_q = 0;
  assign out1_re = n309_o;
  assign out1_im = n310_o;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:23:17  */
  assign n306_o = {in1_im, in1_re};
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:21:17  */
  assign n307_o = {in2_im, in2_re};
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:40:16  */
  assign n309_o = n381_o[47:0];
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:36:16  */
  assign n310_o = n381_o[95:48];
  /* ../fpga-fft/rtl/complex_multiply2.vhd:20:16  */
  assign halflsb = 10'b0100000000; // (signal)
  /* ../fpga-fft/rtl/complex_multiply2.vhd:21:16  */
  assign halflsb1 = n360_o; // (signal)
  /* ../fpga-fft/rtl/complex_multiply2.vhd:22:16  */
  assign a = n316_o; // (signal)
  /* ../fpga-fft/rtl/complex_multiply2.vhd:22:18  */
  assign b = n322_o; // (signal)
  /* ../fpga-fft/rtl/complex_multiply2.vhd:22:23  */
  assign b1 = n383_q; // (signal)
  /* ../fpga-fft/rtl/complex_multiply2.vhd:23:16  */
  assign c = n328_o; // (signal)
  /* ../fpga-fft/rtl/complex_multiply2.vhd:23:18  */
  assign d = n334_o; // (signal)
  /* ../fpga-fft/rtl/complex_multiply2.vhd:23:20  */
  assign c1 = n388_q; // (signal)
  /* ../fpga-fft/rtl/complex_multiply2.vhd:23:23  */
  assign d1 = n389_q; // (signal)
  /* ../fpga-fft/rtl/complex_multiply2.vhd:26:25  */
  assign ac3 = madd1_p; // (signal)
  /* ../fpga-fft/rtl/complex_multiply2.vhd:26:33  */
  assign ad3 = madd2_p; // (signal)
  /* ../fpga-fft/rtl/complex_multiply2.vhd:26:46  */
  assign bd4 = madd3_p; // (signal)
  /* ../fpga-fft/rtl/complex_multiply2.vhd:26:54  */
  assign bc4 = madd4_p; // (signal)
  /* ../fpga-fft/rtl/complex_multiply2.vhd:27:16  */
  assign res_re = n410_q; // (signal)
  /* ../fpga-fft/rtl/complex_multiply2.vhd:27:24  */
  assign res_im = n411_q; // (signal)
  /* ../fpga-fft/rtl/fft_types.vhd:146:30  */
  assign n316_o = n306_o[10:0];
  /* ../fpga-fft/rtl/fft_types.vhd:150:30  */
  assign n322_o = n306_o[58:48];
  /* ../fpga-fft/rtl/fft_types.vhd:146:30  */
  assign n328_o = n307_o[7:0];
  /* ../fpga-fft/rtl/fft_types.vhd:150:30  */
  assign n334_o = n307_o[55:48];
  /* ../fpga-fft/rtl/complex_multiply2.vhd:48:21  */
  assign n360_o = {{9{halflsb[9]}}, halflsb}; // sext
  /* ../fpga-fft/rtl/complex_multiply2.vhd:50:9  */
  multiplyadd_11_8_19_5ba93c9db0cff93f52b521d7420e43f6eda2784f madd1 (
    .clk(clk),
    .a(a),
    .b(c),
    .c(halflsb1),
    .p(madd1_p));
  /* ../fpga-fft/rtl/complex_multiply2.vhd:53:9  */
  multiplyadd_11_8_19_5ba93c9db0cff93f52b521d7420e43f6eda2784f madd2 (
    .clk(clk),
    .a(a),
    .b(d),
    .c(halflsb1),
    .p(madd2_p));
  /* ../fpga-fft/rtl/complex_multiply2.vhd:57:9  */
  multiplyadd_11_8_19_bf8b4530d8d246dd74ac53a13471bba17941dff7 madd3 (
    .clk(clk),
    .a(b1),
    .b(d1),
    .c(ac3),
    .p(madd3_p));
  /* ../fpga-fft/rtl/complex_multiply2.vhd:60:9  */
  multiplyadd_11_8_19_5ba93c9db0cff93f52b521d7420e43f6eda2784f madd4 (
    .clk(clk),
    .a(b1),
    .b(c1),
    .c(ad3),
    .p(madd4_p));
  /* ../fpga-fft/rtl/complex_multiply2.vhd:64:22  */
  assign n365_o = bd4[16:9];
  /* ../fpga-fft/rtl/complex_multiply2.vhd:65:22  */
  assign n368_o = bc4[16:9];
  /* ../fpga-fft/rtl/fft_types.vhd:139:27  */
  assign n377_o = {{40{res_re[7]}}, res_re}; // sext
  /* ../fpga-fft/rtl/fft_types.vhd:140:27  */
  assign n380_o = {{40{res_im[7]}}, res_im}; // sext
  assign n381_o = {n380_o, n377_o};
  /* ../fpga-fft/rtl/complex_multiply2.vhd:34:17  */
  always @(posedge clk)
    n383_q <= b;
  /* ../fpga-fft/rtl/complex_multiply2.vhd:35:17  */
  always @(posedge clk)
    n388_q <= c;
  /* ../fpga-fft/rtl/complex_multiply2.vhd:36:17  */
  always @(posedge clk)
    n389_q <= d;
  /* ../fpga-fft/rtl/complex_multiply2.vhd:64:61  */
  always @(posedge clk)
    n410_q <= n365_o;
  /* ../fpga-fft/rtl/complex_multiply2.vhd:65:61  */
  always @(posedge clk)
    n411_q <= n368_o;
endmodule

module twiddleaddrgen_6_6_7_0e356ba505631fbf715758bed27d503f8b260e3a
  (input  clk,
   input  [11:0] phase,
   input  [5:0] bitpermout,
   output [11:0] twaddr,
   output [5:0] bitpermin);
  reg [11:0] ph0 = 0;
  reg [11:0] ph_twiddle = 0;
  reg [5:0] twmajoraddr = 0;
  reg [11:0] twaddr0 = 0;
  reg [11:0] twaddr0next = 0;
  wire [11:0] n285_o;
  wire [11:0] n287_o;
  wire [5:0] n290_o;
  wire [5:0] n292_o;
  wire [5:0] n293_o;
  wire [5:0] n295_o;
  wire n297_o;
  wire [11:0] n298_o;
  wire [11:0] n299_o;
  wire [11:0] n300_o;
  reg [11:0] n303_q = 0;
  reg [11:0] n305_q = 0;
  assign twaddr = twaddr0;
  assign bitpermin = n290_o;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:36:22  */
  always @*
    ph0 = phase; // (isignal)
  initial
    ph0 = 12'b000000000000;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:38:16  */
  always @*
    ph_twiddle = n303_q; // (isignal)
  initial
    ph_twiddle = 12'b000000000000;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:39:16  */
  always @*
    twmajoraddr = n292_o; // (isignal)
  initial
    twmajoraddr = 6'b000000;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:41:16  */
  always @*
    twaddr0 = n305_q; // (isignal)
  initial
    twaddr0 = 12'b000000000000;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:41:25  */
  always @*
    twaddr0next = n298_o; // (isignal)
  initial
    twaddr0next = 12'b000000000000;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:51:26  */
  assign n285_o = ph0 + 12'b000000000111;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:51:39  */
  assign n287_o = n285_o + 12'b000000000010;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:53:32  */
  assign n290_o = ph_twiddle[11:6];
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:54:35  */
  assign n292_o = 1'b1 ? bitpermout : n293_o;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:55:27  */
  assign n293_o = ph_twiddle[11:6];
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:58:61  */
  assign n295_o = ph_twiddle[5:0];
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:58:83  */
  assign n297_o = n295_o == 6'b000000;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:58:46  */
  assign n298_o = n297_o ? 12'b000000000000 : n300_o;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:59:49  */
  assign n299_o = {6'b0, twmajoraddr};  //  uext
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:59:49  */
  assign n300_o = twaddr0 + n299_o;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:51:42  */
  always @(posedge clk)
    n303_q <= n287_o;
  initial
    n303_q = 12'b000000000000;
  /* ../fpga-fft/rtl/twiddle_addr_gen.vhd:66:32  */
  always @(posedge clk)
    n305_q <= twaddr0next;
  initial
    n305_q = 12'b000000000000;
endmodule

module transposer_6_6_8
  (input  clk,
   input  [47:0] din_re,
   input  [47:0] din_im,
   input  [11:0] phase,
   input  reorderenable,
   output [47:0] dout_re,
   output [47:0] dout_im);
  wire [95:0] n251_o;
  wire [47:0] n253_o;
  wire [47:0] n254_o;
  wire [95:0] din2;
  wire [95:0] dout0;
  wire [95:0] dout1;
  wire [11:0] iaddr;
  wire [11:0] iaddr2;
  wire [11:0] oaddr;
  wire [11:0] gb_addrgen_addr;
  wire [47:0] gb_g4_ram_rddata_re;
  wire [47:0] gb_g4_ram_rddata_im;
  wire [95:0] n256_o;
  localparam n258_o = 1'b1;
  wire [47:0] n259_o;
  wire [47:0] n260_o;
  wire [11:0] gb_sr1_dout;
  localparam n266_o = 1'b1;
  reg [95:0] n271_q = 0;
  reg [95:0] n272_q = 0;
  reg [11:0] n273_q = 0;
  reg [95:0] n274_q = 0;
  assign dout_re = n253_o;
  assign dout_im = n254_o;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:78:51  */
  assign n251_o = {din_im, din_re};
  /* ../fpga-fft/rtl/reorder_buffer.vhd:37:17  */
  assign n253_o = n274_q[47:0];
  /* ../fpga-fft/rtl/reorder_buffer.vhd:34:17  */
  assign n254_o = n274_q[95:48];
  /* ../fpga-fft/rtl/transposer.vhd:31:16  */
  assign din2 = n271_q; // (signal)
  /* ../fpga-fft/rtl/transposer.vhd:31:22  */
  assign dout0 = n256_o; // (signal)
  /* ../fpga-fft/rtl/transposer.vhd:31:29  */
  assign dout1 = n272_q; // (signal)
  /* ../fpga-fft/rtl/transposer.vhd:32:16  */
  assign iaddr = gb_sr1_dout; // (signal)
  /* ../fpga-fft/rtl/transposer.vhd:32:23  */
  assign iaddr2 = n273_q; // (signal)
  /* ../fpga-fft/rtl/transposer.vhd:32:31  */
  assign oaddr = gb_addrgen_addr; // (signal)
  /* ../fpga-fft/rtl/transposer.vhd:47:17  */
  transposer_addrgen_6_6_4 gb_addrgen (
    .clk(clk),
    .reorderenable(reorderenable),
    .phase(phase),
    .addr(gb_addrgen_addr));
  /* ../fpga-fft/rtl/transposer.vhd:56:25  */
  complexram_8_12 gb_g4_ram (
    .rdclk(clk),
    .wrclk(clk),
    .rdaddr(oaddr),
    .wren(n258_o),
    .wraddr(iaddr2),
    .wrdata_re(n259_o),
    .wrdata_im(n260_o),
    .rddata_re(gb_g4_ram_rddata_re),
    .rddata_im(gb_g4_ram_rddata_im));
  assign n256_o = {gb_g4_ram_rddata_im, gb_g4_ram_rddata_re};
  assign n259_o = din2[47:0];
  assign n260_o = din2[95:48];
  /* ../fpga-fft/rtl/transposer.vhd:78:17  */
  sr_unsigned_12_4 gb_sr1 (
    .clk(clk),
    .din(oaddr),
    .ce(n266_o),
    .dout(gb_sr1_dout));
  /* ../fpga-fft/rtl/transposer.vhd:80:29  */
  always @(posedge clk)
    n271_q <= n251_o;
  /* ../fpga-fft/rtl/transposer.vhd:62:40  */
  always @(posedge clk)
    n272_q <= dout0;
  /* ../fpga-fft/rtl/transposer.vhd:81:33  */
  always @(posedge clk)
    n273_q <= iaddr;
  /* ../fpga-fft/rtl/transposer.vhd:71:39  */
  always @(posedge clk)
    n274_q <= dout1;
endmodule

module reorderbuffer_12_8_4_0_0
  (input  clk,
   input  [47:0] din_re,
   input  [47:0] din_im,
   input  [11:0] phase,
   input  [11:0] bitpermout,
   output [47:0] dout_re,
   output [47:0] dout_im,
   output [11:0] bitpermin,
   output [1:0] bitpermcount);
  wire [95:0] n200_o;
  wire [47:0] n202_o;
  wire [47:0] n203_o;
  wire [95:0] din2;
  wire [95:0] dout0;
  wire [11:0] iaddr;
  wire [11:0] iaddr2;
  wire [11:0] oaddr;
  reg [1:0] state = 0;
  reg [1:0] statenext = 0;
  wire [11:0] ph1;
  wire [11:0] ph2;
  wire [11:0] n209_o;
  wire [11:0] n211_o;
  wire n218_o;
  wire [1:0] n219_o;
  wire [1:0] n221_o;
  wire n223_o;
  wire [47:0] g4_ram_rddata_re;
  wire [47:0] g4_ram_rddata_im;
  wire [95:0] n229_o;
  localparam n231_o = 1'b1;
  wire [47:0] n232_o;
  wire [47:0] n233_o;
  wire [11:0] sr1_dout;
  localparam n237_o = 1'b1;
  reg [95:0] n242_q = 0;
  reg [11:0] n243_q = 0;
  reg [11:0] n244_q = 0;
  wire [1:0] n245_o;
  reg [1:0] n246_q = 0;
  reg [11:0] n247_q = 0;
  reg [11:0] n248_q = 0;
  reg [95:0] n250_q = 0;
  assign dout_re = n202_o;
  assign dout_im = n203_o;
  assign bitpermin = ph2;
  assign bitpermcount = state;
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:30:36  */
  assign n200_o = {din_im, din_re};
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:17:17  */
  assign n202_o = n250_q[47:0];
  assign n203_o = n250_q[95:48];
  /* ../fpga-fft/rtl/reorder_buffer.vhd:43:16  */
  assign din2 = n242_q; // (signal)
  /* ../fpga-fft/rtl/reorder_buffer.vhd:43:21  */
  assign dout0 = n229_o; // (signal)
  /* ../fpga-fft/rtl/reorder_buffer.vhd:44:16  */
  assign iaddr = sr1_dout; // (signal)
  /* ../fpga-fft/rtl/reorder_buffer.vhd:44:23  */
  assign iaddr2 = n243_q; // (signal)
  /* ../fpga-fft/rtl/reorder_buffer.vhd:44:31  */
  assign oaddr = n244_q; // (signal)
  /* ../fpga-fft/rtl/reorder_buffer.vhd:53:16  */
  always @*
    state = n246_q; // (isignal)
  initial
    state = 2'b00;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:53:22  */
  always @*
    statenext = n219_o; // (isignal)
  initial
    statenext = 2'b00;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:54:16  */
  assign ph1 = n247_q; // (signal)
  /* ../fpga-fft/rtl/reorder_buffer.vhd:54:20  */
  assign ph2 = n248_q; // (signal)
  /* ../fpga-fft/rtl/reorder_buffer.vhd:57:21  */
  assign n209_o = phase + 12'b000000000110;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:57:33  */
  assign n211_o = n209_o - 12'b000000000000;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:61:46  */
  assign n218_o = $unsigned(state) >= $unsigned(2'b11);
  /* ../fpga-fft/rtl/reorder_buffer.vhd:61:36  */
  assign n219_o = n218_o ? 2'b00 : n221_o;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:61:71  */
  assign n221_o = state + 2'b01;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:62:36  */
  assign n223_o = ph1 == 12'b000000000000;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:77:17  */
  complexram_8_12 g4_ram (
    .rdclk(clk),
    .wrclk(clk),
    .rdaddr(oaddr),
    .wren(n231_o),
    .wraddr(iaddr2),
    .wrdata_re(n232_o),
    .wrdata_im(n233_o),
    .rddata_re(g4_ram_rddata_re),
    .rddata_im(g4_ram_rddata_im));
  assign n229_o = {g4_ram_rddata_im, g4_ram_rddata_re};
  assign n232_o = din2[47:0];
  assign n233_o = din2[95:48];
  /* ../fpga-fft/rtl/reorder_buffer.vhd:96:9  */
  sr_unsigned_12_3 sr1 (
    .clk(clk),
    .din(oaddr),
    .ce(n237_o),
    .dout(sr1_dout));
  /* ../fpga-fft/rtl/reorder_buffer.vhd:98:21  */
  always @(posedge clk)
    n242_q <= n200_o;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:99:25  */
  always @(posedge clk)
    n243_q <= iaddr;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:67:29  */
  always @(posedge clk)
    n244_q <= bitpermout;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:62:28  */
  assign n245_o = n223_o ? statenext : state;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:62:28  */
  always @(posedge clk)
    n246_q <= n245_o;
  initial
    n246_q = 2'b00;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:57:48  */
  always @(posedge clk)
    n247_q <= n211_o;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:60:20  */
  always @(posedge clk)
    n248_q <= ph1;
  /* ../fpga-fft/rtl/reorder_buffer.vhd:84:31  */
  always @(posedge clk)
    n250_q <= dout0;
endmodule

module fft4096_oreorderer1_8
  (input  clk,
   input  [47:0] din_re,
   input  [47:0] din_im,
   input  [11:0] phase,
   output [47:0] dout_re,
   output [47:0] dout_im);
  wire [95:0] n166_o;
  wire [47:0] n168_o;
  wire [47:0] n169_o;
  wire [11:0] rp0;
  wire [11:0] rp1;
  wire rcnt;
  wire [47:0] rb_dout_re;
  wire [47:0] rb_dout_im;
  wire [11:0] rb_bitpermin;
  wire rb_bitpermcount;
  wire [47:0] n170_o;
  wire [47:0] n171_o;
  wire [95:0] n172_o;
  wire n176_o;
  wire n177_o;
  wire [1:0] n178_o;
  wire n179_o;
  wire [2:0] n180_o;
  wire n181_o;
  wire [3:0] n182_o;
  wire n183_o;
  wire [4:0] n184_o;
  wire n185_o;
  wire [5:0] n186_o;
  wire n187_o;
  wire [6:0] n188_o;
  wire n189_o;
  wire [7:0] n190_o;
  wire n191_o;
  wire [8:0] n192_o;
  wire n193_o;
  wire [9:0] n194_o;
  wire n195_o;
  wire [10:0] n196_o;
  wire n197_o;
  wire [11:0] n198_o;
  wire [11:0] n199_o;
  assign dout_re = n168_o;
  assign dout_im = n169_o;
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:130:74  */
  assign n166_o = {din_im, din_re};
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:126:36  */
  assign n168_o = n172_o[47:0];
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:125:66  */
  assign n169_o = n172_o[95:48];
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:21:16  */
  assign rp0 = rb_bitpermin; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:22:16  */
  assign rp1 = n199_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:111  */
  assign rcnt = rb_bitpermcount; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:27:9  */
  reorderbuffer_12_8_2_0_0 rb (
    .clk(clk),
    .din_re(n170_o),
    .din_im(n171_o),
    .phase(phase),
    .bitpermout(rp1),
    .dout_re(rb_dout_re),
    .dout_im(rb_dout_im),
    .bitpermin(rb_bitpermin),
    .bitpermcount(rb_bitpermcount));
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:100:36  */
  assign n170_o = n166_o[47:0];
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:99:33  */
  assign n171_o = n166_o[95:48];
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:85:69  */
  assign n172_o = {rb_dout_im, rb_dout_re};
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:19  */
  assign n176_o = rp0[0];
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:26  */
  assign n177_o = rp0[1];
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:22  */
  assign n178_o = {n176_o, n177_o};
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:33  */
  assign n179_o = rp0[2];
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:29  */
  assign n180_o = {n178_o, n179_o};
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:40  */
  assign n181_o = rp0[3];
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:36  */
  assign n182_o = {n180_o, n181_o};
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:47  */
  assign n183_o = rp0[4];
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:43  */
  assign n184_o = {n182_o, n183_o};
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:54  */
  assign n185_o = rp0[5];
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:50  */
  assign n186_o = {n184_o, n185_o};
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:61  */
  assign n187_o = rp0[6];
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:57  */
  assign n188_o = {n186_o, n187_o};
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:68  */
  assign n189_o = rp0[7];
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:64  */
  assign n190_o = {n188_o, n189_o};
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:75  */
  assign n191_o = rp0[8];
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:71  */
  assign n192_o = {n190_o, n191_o};
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:82  */
  assign n193_o = rp0[9];
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:78  */
  assign n194_o = {n192_o, n193_o};
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:89  */
  assign n195_o = rp0[10];
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:85  */
  assign n196_o = {n194_o, n195_o};
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:97  */
  assign n197_o = rp0[11];
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:93  */
  assign n198_o = {n196_o, n197_o};
  /* ../fpga-fft/generated/fft4096/fft4096_oreorderer1.vhd:31:102  */
  assign n199_o = rcnt ? n198_o : rp0;
endmodule

module fft4096_8_10_bf8b4530d8d246dd74ac53a13471bba17941dff7
  (input  clk,
   input  [47:0] din_re,
   input  [47:0] din_im,
   input  [11:0] phase,
   output [47:0] dout_re,
   output [47:0] dout_im);
  wire [95:0] n90_o;
  wire [47:0] n92_o;
  wire [47:0] n93_o;
  wire [95:0] sub1din;
  wire [95:0] sub1dout;
  wire [95:0] sub2din;
  wire [95:0] sub2dout;
  wire [5:0] sub1phase;
  wire [5:0] sub2phase;
  wire [11:0] ph1;
  wire [11:0] ph2;
  wire [11:0] ph3;
  wire [95:0] rbin;
  wire [95:0] transpout;
  wire [5:0] bitpermin;
  wire [5:0] bitpermout;
  wire [11:0] twaddr;
  wire [95:0] twdata;
  wire [8:0] romaddr;
  wire [17:0] romdata;
  wire [5:0] rp0;
  wire [5:0] rp1;
  wire rcnt;
  wire [5:0] rbinphase;
  wire [5:0] n94_o;
  wire [11:0] n96_o;
  wire [11:0] n98_o;
  wire [47:0] transp_dout_re;
  wire [47:0] transp_dout_im;
  wire [47:0] n101_o;
  wire [47:0] n102_o;
  wire [95:0] n103_o;
  localparam n105_o = 1'b1;
  wire [11:0] twag_twaddr;
  wire [5:0] twag_bitpermin;
  wire [47:0] twmult_out1_re;
  wire [47:0] twmult_out1_im;
  wire [47:0] n108_o;
  wire [47:0] n109_o;
  wire [47:0] n110_o;
  wire [47:0] n111_o;
  wire [95:0] n112_o;
  wire [11:0] n115_o;
  wire [11:0] n117_o;
  wire [5:0] n120_o;
  wire n121_o;
  wire n122_o;
  wire [1:0] n123_o;
  wire n124_o;
  wire [2:0] n125_o;
  wire n126_o;
  wire [3:0] n127_o;
  wire n128_o;
  wire [4:0] n129_o;
  wire n130_o;
  wire [5:0] n131_o;
  wire [47:0] tw_rddata_re;
  wire [47:0] tw_rddata_im;
  wire [8:0] tw_romaddr;
  wire [95:0] n132_o;
  wire [17:0] rom_romdata;
  wire n136_o;
  wire n137_o;
  wire [1:0] n138_o;
  wire n139_o;
  wire [2:0] n140_o;
  wire n141_o;
  wire [3:0] n142_o;
  wire n143_o;
  wire [4:0] n144_o;
  wire n145_o;
  wire [5:0] n146_o;
  wire [5:0] n147_o;
  wire [47:0] rb_dout_re;
  wire [47:0] rb_dout_im;
  wire [5:0] rb_bitpermin;
  wire rb_bitpermcount;
  wire [47:0] n148_o;
  wire [47:0] n149_o;
  wire [95:0] n150_o;
  wire [5:0] n155_o;
  wire [47:0] sub1_dout_re;
  wire [47:0] sub1_dout_im;
  wire [47:0] n156_o;
  wire [47:0] n157_o;
  wire [95:0] n158_o;
  wire [47:0] sub2_dout_re;
  wire [47:0] sub2_dout_im;
  wire [47:0] n160_o;
  wire [47:0] n161_o;
  wire [95:0] n162_o;
  reg [11:0] n164_q = 0;
  reg [11:0] n165_q = 0;
  assign dout_re = n92_o;
  assign dout_im = n93_o;
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:31:36  */
  assign n90_o = {din_im, din_re};
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:17:17  */
  assign n92_o = sub2dout[47:0];
  assign n93_o = sub2dout[95:48];
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:46:16  */
  assign sub1din = n90_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:46:25  */
  assign sub1dout = n158_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:46:35  */
  assign sub2din = n150_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:46:44  */
  assign sub2dout = n162_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:47:16  */
  assign sub1phase = n94_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:48:16  */
  assign sub2phase = n155_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:62:16  */
  assign ph1 = n164_q; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:62:21  */
  assign ph2 = ph1; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:62:26  */
  assign ph3 = n165_q; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:63:16  */
  assign rbin = n112_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:63:22  */
  assign transpout = n103_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:64:16  */
  assign bitpermin = twag_bitpermin; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:64:26  */
  assign bitpermout = n131_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:67:16  */
  assign twaddr = twag_twaddr; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:68:16  */
  assign twdata = n132_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:70:16  */
  assign romaddr = tw_romaddr; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:71:16  */
  assign romdata = rom_romdata; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:72:16  */
  assign rp0 = rb_bitpermin; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:73:16  */
  assign rp1 = n147_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:120:67  */
  assign rcnt = rb_bitpermcount; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:75:16  */
  assign rbinphase = n120_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:79:27  */
  assign n94_o = phase[5:0];
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:81:21  */
  assign n96_o = phase - 12'b000001101111;
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:81:25  */
  assign n98_o = n96_o + 12'b000000000001;
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:83:9  */
  transposer_6_6_8 transp (
    .clk(clk),
    .din_re(n101_o),
    .din_im(n102_o),
    .phase(ph1),
    .reorderenable(n105_o),
    .dout_re(transp_dout_re),
    .dout_im(transp_dout_im));
  assign n101_o = sub1dout[47:0];
  assign n102_o = sub1dout[95:48];
  assign n103_o = {transp_dout_im, transp_dout_re};
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:89:9  */
  twiddleaddrgen_6_6_7_0e356ba505631fbf715758bed27d503f8b260e3a twag (
    .clk(clk),
    .phase(ph2),
    .bitpermout(bitpermout),
    .twaddr(twag_twaddr),
    .bitpermin(twag_bitpermin));
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:103:9  */
  complexmultiply2_11_8_8_bf8b4530d8d246dd74ac53a13471bba17941dff7 twmult (
    .clk(clk),
    .in1_re(n108_o),
    .in1_im(n109_o),
    .in2_re(n110_o),
    .in2_im(n111_o),
    .out1_re(twmult_out1_re),
    .out1_im(twmult_out1_im));
  assign n108_o = twdata[47:0];
  assign n109_o = twdata[95:48];
  assign n110_o = transpout[47:0];
  assign n111_o = transpout[95:48];
  assign n112_o = {twmult_out1_im, twmult_out1_re};
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:109:19  */
  assign n115_o = ph2 - 12'b000000000101;
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:109:21  */
  assign n117_o = n115_o + 12'b000000000001;
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:110:25  */
  assign n120_o = ph3[5:0];
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:112:32  */
  assign n121_o = bitpermin[0];
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:112:45  */
  assign n122_o = bitpermin[1];
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:112:35  */
  assign n123_o = {n121_o, n122_o};
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:112:58  */
  assign n124_o = bitpermin[2];
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:112:48  */
  assign n125_o = {n123_o, n124_o};
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:112:71  */
  assign n126_o = bitpermin[3];
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:112:61  */
  assign n127_o = {n125_o, n126_o};
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:112:84  */
  assign n128_o = bitpermin[4];
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:112:74  */
  assign n129_o = {n127_o, n128_o};
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:112:97  */
  assign n130_o = bitpermin[5];
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:112:87  */
  assign n131_o = {n129_o, n130_o};
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:114:9  */
  twiddlegenerator_10_12_2_3f29546453678b855931c174a97d6c0894b8f546 tw (
    .clk(clk),
    .rdaddr(twaddr),
    .romdata(romdata),
    .rddata_re(tw_rddata_re),
    .rddata_im(tw_rddata_im),
    .romaddr(tw_romaddr));
  assign n132_o = {tw_rddata_im, tw_rddata_re};
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:118:9  */
  twiddlerom4096_10 rom (
    .clk(clk),
    .romaddr(romaddr),
    .romdata(rom_romdata));
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:120:19  */
  assign n136_o = rp0[0];
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:120:26  */
  assign n137_o = rp0[1];
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:120:22  */
  assign n138_o = {n136_o, n137_o};
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:120:33  */
  assign n139_o = rp0[2];
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:120:29  */
  assign n140_o = {n138_o, n139_o};
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:120:40  */
  assign n141_o = rp0[3];
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:120:36  */
  assign n142_o = {n140_o, n141_o};
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:120:47  */
  assign n143_o = rp0[4];
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:120:43  */
  assign n144_o = {n142_o, n143_o};
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:120:54  */
  assign n145_o = rp0[5];
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:120:50  */
  assign n146_o = {n144_o, n145_o};
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:120:58  */
  assign n147_o = rcnt ? n146_o : rp0;
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:123:9  */
  reorderbuffer_6_8_2_0_0 rb (
    .clk(clk),
    .din_re(n148_o),
    .din_im(n149_o),
    .phase(rbinphase),
    .bitpermout(rp1),
    .dout_re(rb_dout_re),
    .dout_im(rb_dout_im),
    .bitpermin(rb_bitpermin),
    .bitpermcount(rb_bitpermcount));
  assign n148_o = rbin[47:0];
  assign n149_o = rbin[95:48];
  assign n150_o = {rb_dout_im, rb_dout_re};
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:128:31  */
  assign n155_o = rbinphase - 6'b000000;
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:129:9  */
  fft4096_sub64_8_10_bf8b4530d8d246dd74ac53a13471bba17941dff7 sub1 (
    .clk(clk),
    .din_re(n156_o),
    .din_im(n157_o),
    .phase(sub1phase),
    .dout_re(sub1_dout_re),
    .dout_im(sub1_dout_im));
  assign n156_o = sub1din[47:0];
  assign n157_o = sub1din[95:48];
  assign n158_o = {sub1_dout_im, sub1_dout_re};
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:131:9  */
  fft4096_sub64_2_8_10_bf8b4530d8d246dd74ac53a13471bba17941dff7 sub2 (
    .clk(clk),
    .din_re(n160_o),
    .din_im(n161_o),
    .phase(sub2phase),
    .dout_re(sub2_dout_re),
    .dout_im(sub2_dout_im));
  assign n160_o = sub2din[47:0];
  assign n161_o = sub2din[95:48];
  assign n162_o = {sub2_dout_im, sub2_dout_re};
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:81:28  */
  always @(posedge clk)
    n164_q <= n98_o;
  /* ../fpga-fft/generated/fft4096/fft4096.vhd:109:24  */
  always @(posedge clk)
    n165_q <= n117_o;
endmodule

module fft4096_ireorderer1_8
  (input  clk,
   input  [47:0] din_re,
   input  [47:0] din_im,
   input  [11:0] phase,
   output [47:0] dout_re,
   output [47:0] dout_im);
  wire [95:0] n30_o;
  wire [47:0] n32_o;
  wire [47:0] n33_o;
  wire [11:0] rp0;
  wire [11:0] rp1;
  wire [11:0] rp2;
  wire [1:0] rcnt;
  wire [47:0] rb_dout_re;
  wire [47:0] rb_dout_im;
  wire [11:0] rb_bitpermin;
  wire [1:0] rb_bitpermcount;
  wire [47:0] n34_o;
  wire [47:0] n35_o;
  wire [95:0] n36_o;
  wire n40_o;
  wire n41_o;
  wire [1:0] n42_o;
  wire n43_o;
  wire [2:0] n44_o;
  wire n45_o;
  wire [3:0] n46_o;
  wire n47_o;
  wire [4:0] n48_o;
  wire n49_o;
  wire [5:0] n50_o;
  wire n51_o;
  wire [6:0] n52_o;
  wire n53_o;
  wire [7:0] n54_o;
  wire n55_o;
  wire [8:0] n56_o;
  wire n57_o;
  wire [9:0] n58_o;
  wire n59_o;
  wire [10:0] n60_o;
  wire n61_o;
  wire [11:0] n62_o;
  wire n63_o;
  wire [11:0] n64_o;
  wire n65_o;
  wire n66_o;
  wire [1:0] n67_o;
  wire n68_o;
  wire [2:0] n69_o;
  wire n70_o;
  wire [3:0] n71_o;
  wire n72_o;
  wire [4:0] n73_o;
  wire n74_o;
  wire [5:0] n75_o;
  wire n76_o;
  wire [6:0] n77_o;
  wire n78_o;
  wire [7:0] n79_o;
  wire n80_o;
  wire [8:0] n81_o;
  wire n82_o;
  wire [9:0] n83_o;
  wire n84_o;
  wire [10:0] n85_o;
  wire n86_o;
  wire [11:0] n87_o;
  wire n88_o;
  wire [11:0] n89_o;
  assign dout_re = n32_o;
  assign dout_im = n33_o;
  /* ../fpga-fft/generated/fft4096/fft4096_wrapper1.vhd:36:91  */
  assign n30_o = {din_im, din_re};
  /* ../fpga-fft/generated/fft4096/fft4096_wrapper1.vhd:21:17  */
  assign n32_o = n36_o[47:0];
  /* ../fpga-fft/generated/fft4096/fft4096_wrapper1.vhd:38:51  */
  assign n33_o = n36_o[95:48];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:21:16  */
  assign rp0 = rb_bitpermin; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:22:16  */
  assign rp1 = n64_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:23:16  */
  assign rp2 = n89_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:24:16  */
  assign rcnt = rb_bitpermcount; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:28:9  */
  reorderbuffer_12_8_4_0_0 rb (
    .clk(clk),
    .din_re(n34_o),
    .din_im(n35_o),
    .phase(phase),
    .bitpermout(rp2),
    .dout_re(rb_dout_re),
    .dout_im(rb_dout_im),
    .bitpermin(rb_bitpermin),
    .bitpermcount(rb_bitpermcount));
  assign n34_o = n30_o[47:0];
  assign n35_o = n30_o[95:48];
  assign n36_o = {rb_dout_im, rb_dout_re};
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:19  */
  assign n40_o = rp0[0];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:26  */
  assign n41_o = rp0[1];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:22  */
  assign n42_o = {n40_o, n41_o};
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:33  */
  assign n43_o = rp0[2];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:29  */
  assign n44_o = {n42_o, n43_o};
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:40  */
  assign n45_o = rp0[3];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:36  */
  assign n46_o = {n44_o, n45_o};
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:47  */
  assign n47_o = rp0[4];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:43  */
  assign n48_o = {n46_o, n47_o};
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:54  */
  assign n49_o = rp0[5];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:50  */
  assign n50_o = {n48_o, n49_o};
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:61  */
  assign n51_o = rp0[11];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:57  */
  assign n52_o = {n50_o, n51_o};
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:69  */
  assign n53_o = rp0[10];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:65  */
  assign n54_o = {n52_o, n53_o};
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:77  */
  assign n55_o = rp0[9];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:73  */
  assign n56_o = {n54_o, n55_o};
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:84  */
  assign n57_o = rp0[8];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:80  */
  assign n58_o = {n56_o, n57_o};
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:91  */
  assign n59_o = rp0[7];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:87  */
  assign n60_o = {n58_o, n59_o};
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:98  */
  assign n61_o = rp0[6];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:94  */
  assign n62_o = {n60_o, n61_o};
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:111  */
  assign n63_o = rcnt[0];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:32:102  */
  assign n64_o = n63_o ? n62_o : rp0;
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:19  */
  assign n65_o = rp1[6];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:26  */
  assign n66_o = rp1[7];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:22  */
  assign n67_o = {n65_o, n66_o};
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:33  */
  assign n68_o = rp1[8];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:29  */
  assign n69_o = {n67_o, n68_o};
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:40  */
  assign n70_o = rp1[9];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:36  */
  assign n71_o = {n69_o, n70_o};
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:47  */
  assign n72_o = rp1[10];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:43  */
  assign n73_o = {n71_o, n72_o};
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:55  */
  assign n74_o = rp1[11];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:51  */
  assign n75_o = {n73_o, n74_o};
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:63  */
  assign n76_o = rp1[0];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:59  */
  assign n77_o = {n75_o, n76_o};
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:70  */
  assign n78_o = rp1[1];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:66  */
  assign n79_o = {n77_o, n78_o};
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:77  */
  assign n80_o = rp1[2];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:73  */
  assign n81_o = {n79_o, n80_o};
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:84  */
  assign n82_o = rp1[3];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:80  */
  assign n83_o = {n81_o, n82_o};
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:91  */
  assign n84_o = rp1[4];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:87  */
  assign n85_o = {n83_o, n84_o};
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:98  */
  assign n86_o = rp1[5];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:94  */
  assign n87_o = {n85_o, n86_o};
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:111  */
  assign n88_o = rcnt[1];
  /* ../fpga-fft/generated/fft4096/fft4096_ireorderer1.vhd:33:102  */
  assign n89_o = n88_o ? n87_o : rp1;
endmodule

module fft4096_wrapper1
  (input  clk,
   input  [47:0] din_re,
   input  [47:0] din_im,
   input  [11:0] phase,
   output [47:0] dout_re,
   output [47:0] dout_im);
  wire [95:0] n0_o;
  wire [47:0] n2_o;
  wire [47:0] n3_o;
  wire [95:0] core_din;
  wire [95:0] core_dout;
  wire [11:0] core_phase;
  wire [11:0] oreorderer_phase;
  wire [47:0] ireorder_dout_re;
  wire [47:0] ireorder_dout_im;
  wire [47:0] n4_o;
  wire [47:0] n5_o;
  wire [95:0] n6_o;
  wire [11:0] n9_o;
  wire [11:0] n11_o;
  wire [47:0] core_dout_re;
  wire [47:0] core_dout_im;
  wire [47:0] n14_o;
  wire [47:0] n15_o;
  wire [95:0] n16_o;
  wire [11:0] n19_o;
  wire [11:0] n21_o;
  wire [47:0] oreorderer_dout_re;
  wire [47:0] oreorderer_dout_im;
  wire [47:0] n24_o;
  wire [47:0] n25_o;
  wire [95:0] n26_o;
  reg [11:0] n28_q = 0;
  reg [11:0] n29_q = 0;
  assign dout_re = n2_o;
  assign dout_im = n3_o;
  assign n0_o = {din_im, din_re};
  assign n2_o = n26_o[47:0];
  assign n3_o = n26_o[95:48];
  /* ../fpga-fft/generated/fft4096/fft4096_wrapper1.vhd:25:16  */
  assign core_din = n6_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_wrapper1.vhd:25:26  */
  assign core_dout = n16_o; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_wrapper1.vhd:36:53  */
  assign core_phase = n28_q; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_wrapper1.vhd:27:16  */
  assign oreorderer_phase = n29_q; // (signal)
  /* ../fpga-fft/generated/fft4096/fft4096_wrapper1.vhd:30:9  */
  fft4096_ireorderer1_8 ireorder (
    .clk(clk),
    .din_re(n4_o),
    .din_im(n5_o),
    .phase(phase),
    .dout_re(ireorder_dout_re),
    .dout_im(ireorder_dout_im));
  assign n4_o = n0_o[47:0];
  assign n5_o = n0_o[95:48];
  assign n6_o = {ireorder_dout_im, ireorder_dout_re};
  /* ../fpga-fft/generated/fft4096/fft4096_wrapper1.vhd:33:29  */
  assign n9_o = phase - 12'b000000000000;
  /* ../fpga-fft/generated/fft4096/fft4096_wrapper1.vhd:33:36  */
  assign n11_o = n9_o + 12'b000000000001;
  /* ../fpga-fft/generated/fft4096/fft4096_wrapper1.vhd:35:9  */
  fft4096_8_10_bf8b4530d8d246dd74ac53a13471bba17941dff7 core (
    .clk(clk),
    .din_re(n14_o),
    .din_im(n15_o),
    .phase(core_phase),
    .dout_re(core_dout_re),
    .dout_im(core_dout_im));
  assign n14_o = core_din[47:0];
  assign n15_o = core_din[95:48];
  assign n16_o = {core_dout_im, core_dout_re};
  /* ../fpga-fft/generated/fft4096/fft4096_wrapper1.vhd:38:40  */
  assign n19_o = core_phase - 12'b000100100011;
  /* ../fpga-fft/generated/fft4096/fft4096_wrapper1.vhd:38:47  */
  assign n21_o = n19_o + 12'b000000000001;
  /* ../fpga-fft/generated/fft4096/fft4096_wrapper1.vhd:40:9  */
  fft4096_oreorderer1_8 oreorderer (
    .clk(clk),
    .din_re(n24_o),
    .din_im(n25_o),
    .phase(oreorderer_phase),
    .dout_re(oreorderer_dout_re),
    .dout_im(oreorderer_dout_im));
  assign n24_o = core_dout[47:0];
  assign n25_o = core_dout[95:48];
  assign n26_o = {oreorderer_dout_im, oreorderer_dout_re};
  /* ../fpga-fft/generated/fft4096/fft4096_wrapper1.vhd:33:40  */
  always @(posedge clk)
    n28_q <= n11_o;
  /* ../fpga-fft/generated/fft4096/fft4096_wrapper1.vhd:38:51  */
  always @(posedge clk)
    n29_q <= n21_o;
endmodule

