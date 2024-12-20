# From: https://grittyengineer.com/creating-vivado-ip-the-smart-tcl-way/

# User guide: https://docs.amd.com/v/u/en-US/pg105-cordic

# Resources from OOC run on XC7S15:
# 484 LUT
# 510 FF

# Check IP
if { [file isdirectory "IP/CordicSinCos"] } {
    # if the IP files exist, we already generated the IP, so we can just
    # read the ip definition (.xci)
    read_ip IP/CordicSinCos/CordicSinCos.xci
} else {
    # IP folder does not exist. Create IP folder
    file mkdir IP

    # create_ip requires that a project is open in memory. Create project 
    # but don't do anything with it
    # create_project -in_memory

    # paste commands from Journal file to recreate IP
    create_ip -name cordic -vendor xilinx.com -library ip -version 6.0 -module_name CordicSinCos -dir IP

    set_property -dict [list \
        CONFIG.Functional_Selection {Sin_and_Cos} \
        CONFIG.Pipelining_Mode {Optimal} \
        CONFIG.Phase_Format {Scaled_Radians} \
        CONFIG.Input_Width {12} \
        CONFIG.Output_Width {9} \
        CONFIG.Round_Mode {Round_Pos_Neg_Inf} \
        CONFIG.flow_control {Blocking} \
        CONFIG.optimize_goal {Resources} \
        CONFIG.ACLKEN {false} \
        CONFIG.ARESETN {true} \
        CONFIG.Data_Format {SignedFraction} \
        CONFIG.phase_has_tuser {true} \
        CONFIG.phase_tuser_width {3} \
        CONFIG.out_tready {true} \
    ] [get_ips CordicSinCos]

    generate_target all [get_ips]

    # Synthesize all the IP
    synth_ip [get_ips]
}
