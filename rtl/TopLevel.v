// Generator : SpinalHDL v1.10.2    git head : 279867b771fb50fc0aec21d8a20d8fdad0f87e3f
// Component : TopLevel
// Git hash  : f3ef2ed4de80f6de6024e0f8951969d4c2aca5f1

`timescale 1ns/1ps

module TopLevel (
  output reg           io_result,
  output wire [7:0]    io_counterOut,
  input  wire          clk,
  input  wire          reset
);
  localparam fsm_enumDef_BOOT = 2'd0;
  localparam fsm_enumDef_IDLE = 2'd1;
  localparam fsm_enumDef_RUN = 2'd2;
  localparam fsm_enumDef_DONE = 2'd3;

  wire                fsm_wantExit;
  reg                 fsm_wantStart;
  wire                fsm_wantKill;
  reg        [7:0]    fsm_counter;
  reg        [1:0]    fsm_stateReg;
  reg        [1:0]    fsm_stateNext;
  wire                when_counter_l27;
  wire                when_StateMachine_l253;
  wire                when_StateMachine_l253_1;
  `ifndef SYNTHESIS
  reg [31:0] fsm_stateReg_string;
  reg [31:0] fsm_stateNext_string;
  `endif


  `ifndef SYNTHESIS
  always @(*) begin
    case(fsm_stateReg)
      fsm_enumDef_BOOT : fsm_stateReg_string = "BOOT";
      fsm_enumDef_IDLE : fsm_stateReg_string = "IDLE";
      fsm_enumDef_RUN : fsm_stateReg_string = "RUN ";
      fsm_enumDef_DONE : fsm_stateReg_string = "DONE";
      default : fsm_stateReg_string = "????";
    endcase
  end
  always @(*) begin
    case(fsm_stateNext)
      fsm_enumDef_BOOT : fsm_stateNext_string = "BOOT";
      fsm_enumDef_IDLE : fsm_stateNext_string = "IDLE";
      fsm_enumDef_RUN : fsm_stateNext_string = "RUN ";
      fsm_enumDef_DONE : fsm_stateNext_string = "DONE";
      default : fsm_stateNext_string = "????";
    endcase
  end
  `endif

  assign fsm_wantExit = 1'b0;
  always @(*) begin
    fsm_wantStart = 1'b0;
    case(fsm_stateReg)
      fsm_enumDef_IDLE : begin
      end
      fsm_enumDef_RUN : begin
      end
      fsm_enumDef_DONE : begin
      end
      default : begin
        fsm_wantStart = 1'b1;
      end
    endcase
  end

  assign fsm_wantKill = 1'b0;
  always @(*) begin
    io_result = 1'b0;
    if(when_StateMachine_l253_1) begin
      io_result = 1'b1;
    end
  end

  assign io_counterOut = fsm_counter;
  always @(*) begin
    fsm_stateNext = fsm_stateReg;
    case(fsm_stateReg)
      fsm_enumDef_IDLE : begin
        fsm_stateNext = fsm_enumDef_RUN;
      end
      fsm_enumDef_RUN : begin
        if(when_counter_l27) begin
          fsm_stateNext = fsm_enumDef_DONE;
        end
      end
      fsm_enumDef_DONE : begin
      end
      default : begin
      end
    endcase
    if(fsm_wantStart) begin
      fsm_stateNext = fsm_enumDef_IDLE;
    end
    if(fsm_wantKill) begin
      fsm_stateNext = fsm_enumDef_BOOT;
    end
  end

  assign when_counter_l27 = (fsm_counter == 8'h0f);
  assign when_StateMachine_l253 = ((! (fsm_stateReg == fsm_enumDef_IDLE)) && (fsm_stateNext == fsm_enumDef_IDLE));
  assign when_StateMachine_l253_1 = ((! (fsm_stateReg == fsm_enumDef_DONE)) && (fsm_stateNext == fsm_enumDef_DONE));
  always @(posedge clk or posedge reset) begin
    if(reset) begin
      fsm_counter <= 8'h0;
      fsm_stateReg <= fsm_enumDef_BOOT;
    end else begin
      fsm_stateReg <= fsm_stateNext;
      case(fsm_stateReg)
        fsm_enumDef_IDLE : begin
        end
        fsm_enumDef_RUN : begin
          fsm_counter <= (fsm_counter + 8'h01);
        end
        fsm_enumDef_DONE : begin
        end
        default : begin
        end
      endcase
      if(when_StateMachine_l253) begin
        fsm_counter <= 8'h0;
      end
    end
  end


endmodule
